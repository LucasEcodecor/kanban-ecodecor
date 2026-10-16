import shutil
import socket
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
import streamlit as st
from fake_supabase import BancoFake, modulo_fake

ROOT = Path(__file__).resolve().parents[1]


class Interface(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='kanban_ficticio_')
        app = Path(self.tmp.name) / 'kanban_equipe.py'
        shutil.copy2(ROOT / 'kanban_equipe.py', app)
        self.banco = BancoFake()
        self.fake = patch.dict(sys.modules, {'supabase': modulo_fake(self.banco)})
        self.fake.start()
        self.rede = patch.object(socket.socket, 'connect', side_effect=AssertionError('Rede proibida nos testes'))
        self.rede.start()
        st.cache_data.clear()
        self.at = AppTest.from_file(str(app), default_timeout=15).run()
        self.assertEqual(len(self.at.exception), 0)
    def tearDown(self):
        self.rede.stop()
        self.fake.stop()
        st.cache_data.clear()
        self.tmp.cleanup()
    def botao(self, label):
        return next(b for b in self.at.button if b.label == label)
    def seletor(self, label):
        return next(s for s in self.at.selectbox if s.label == label)

    def test_avisos_fechados_apos_atualizar(self):
        avisos = [e for e in self.at.expander if 'Notificações' in e.label]
        self.assertEqual(len(avisos), 1)
        self.assertFalse(avisos[0].proto.expanded)
        self.botao('🔄 Atualizar').click().run()
        self.assertFalse(next(e for e in self.at.expander if 'Notificações' in e.label).proto.expanded)
        self.assertEqual(self.banco.gravacoes, [])

    def test_filtros_sem_gravar_e_sem_reordenar_lista_filtrada(self):
        self.assertIn('Situação', [s.label for s in self.at.selectbox])
        self.seletor('Situação').select('Em andamento').run()
        self.assertEqual(len([b for b in self.at.button if b.label == '📄 Etiquetas']), 7)
        self.assertTrue(all(b.disabled for b in self.at.button if b.label in ('⬆️ Subir', '⬇️ Descer')))
        self.assertEqual(self.banco.gravacoes, [])

    def test_paginacao_da_busca_nao_volta_para_primeira(self):
        self.at.text_input(key='busca_demanda').set_value('FICTÍCIO').run()
        self.botao('Página ➡').click().run()
        self.assertEqual(self.at.session_state['pagina_atual'], 2)
        self.assertEqual(self.banco.gravacoes, [])

    def test_etiquetas_e_voltar(self):
        next(b for b in self.at.button if b.label == '📄 Etiquetas').click().run()
        self.assertEqual(len(self.at.exception), 0)
        self.assertIn('QUANTIDADE: 43 unidades', self.at.code[0].value)
        self.botao('❌ Voltar ao painel').click().run()
        self.assertEqual(self.at.session_state['modo_demanda'], 'lista')
        self.assertEqual(self.banco.gravacoes, [])

    def test_formulario_etapas_persistente(self):
        self.at.checkbox(key='chk_1_0').check()
        next(b for b in self.at.button if b.label == '💾 Salvar etapas').click().run()
        self.assertEqual(len(self.at.exception), 0)
        self.assertTrue(self.banco.dados[0]['etapas']['ETIQUETAS (LUCAS)'])
        self.assertEqual(len(self.banco.gravacoes), 1)

    def test_cadastro_bigodinho_em_banco_ficticio(self):
        self.botao('➕ Nova demanda').click().run()
        self.assertEqual(self.at.radio[0].value, 'Cliente normal')
        self.at.radio[0].set_value('Etiqueta personalizada Bigodinho').run()
        self.assertEqual(self.seletor('Medida:').options, ['60x40', '80x50'])
        self.seletor('Medida:').select('80x50')
        self.at.number_input[0].set_value(20)
        self.botao('➕ Adicionar medida').click().run()
        next(t for t in self.at.text_input if t.label == 'Número da NF:').set_value('NOVA-TESTE')
        self.botao('✅ Salvar demanda').click().run()
        self.assertEqual(len(self.at.exception), 0)
        nova = next(d for d in self.banco.dados if d['nf'] == 'NOVA-TESTE')
        self.assertEqual(nova['cliente'], 'GALPAO DROP LTDA (BIGODINHO)')
        self.assertEqual(nova['itens'], [{'tam': '80x50', 'qtd': 20}])
        self.assertEqual(self.at.session_state['modo_demanda'], 'lista')

    def test_edicao_preserva_itens_e_etapas(self):
        import copy
        anterior = copy.deepcopy(self.banco.dados[1])
        # AppTest 1.56 mantém elementos antigos ao fazer rerun dentro de card.
        # Renderiza o estado de edição isolado; a navegação é conferida no navegador.
        self.at = AppTest.from_file(str(Path(self.tmp.name) / 'kanban_equipe.py'), default_timeout=15)
        self.at.session_state['modo_demanda'] = 'editar'
        self.at.session_state['demanda_edit'] = copy.deepcopy(anterior)
        self.at.session_state['itens_temp'] = copy.deepcopy(anterior['itens'])
        self.at.run()
        next(t for t in self.at.text_input if t.label == 'Agendamento:').set_value('AMANHÃ')
        self.botao('✅ Salvar demanda').click().run()
        atual = self.banco.dados[1]
        self.assertEqual(len(self.at.exception), 0)
        self.assertEqual(atual['agendamento'], 'AMANHÃ')
        self.assertEqual(atual['itens'], anterior['itens'])
        self.assertEqual(atual['etapas'], anterior['etapas'])
        self.assertEqual(atual['data'], anterior['data'])

    def test_resultado_vazio_e_retorno_do_filtro(self):
        self.seletor('Situação').select('Pendentes').run()
        self.seletor('Etapa concluída').select('ETIQUETAS (LUCAS)').run()
        self.assertEqual(len(self.at.exception), 0)
        self.assertEqual(len([b for b in self.at.button if b.label == '📄 Etiquetas']), 0)
        self.seletor('Etapa concluída').select('Todas').run()
        self.assertEqual(len([b for b in self.at.button if b.label == '📄 Etiquetas']), 7)

    def test_html_dos_cards_e_avisos_escapado(self):
        self.banco.dados[0]['cliente'] = '<b>CLIENTE DE TESTE</b>'
        self.banco.dados[0]['nf'] = '<em>NF TESTE</em>'
        self.botao('🔄 Atualizar').click().run()
        cards = [m.value for m in self.at.markdown if 'demand-title' in m.value and '<style>' not in m.value]
        self.assertTrue(any('&lt;b&gt;CLIENTE DE TESTE&lt;/b&gt;' in m for m in cards))
        self.assertFalse(any('<b>CLIENTE DE TESTE</b>' in m for m in cards))
        meta = [m.value for m in self.at.markdown if "class='demand-meta'" in m.value]
        self.assertTrue(any('&lt;em&gt;NF TESTE&lt;/em&gt;' in m for m in meta))

    def test_busca_encontra_outro_dia_quando_dia_selecionado_vazio(self):
        import datetime
        self.at.date_input[0].set_value(datetime.date.today() + datetime.timedelta(days=2)).run()
        self.at.text_input(key='busca_demanda').set_value('TESTE001').run()
        self.assertEqual(len(self.at.exception), 0)
        self.assertEqual(len([b for b in self.at.button if b.label == '📄 Etiquetas']), 1)

    def test_reordenacao_no_dia_sem_filtro_continua_disponivel(self):
        self.at.button(key='down_1').click().run()
        self.assertEqual(len(self.at.exception), 0)
        self.assertEqual(self.banco.dados[0]['ordem'], 2)
        self.assertEqual(self.banco.dados[1]['ordem'], 1)
        self.assertEqual(len(self.banco.gravacoes), 2)


if __name__ == '__main__':
    unittest.main()
