"""Edição de data em banco fictício: nenhuma conexão real é permitida."""
import copy
import datetime
from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest
import test_interface


class EdicaoData(unittest.TestCase):
    setUp = test_interface.Interface.setUp
    tearDown = test_interface.Interface.tearDown
    botao = test_interface.Interface.botao

    def abrir_edicao(self, indice=1):
        demanda = copy.deepcopy(self.banco.dados[indice])
        self.at = AppTest.from_file(str(Path(self.tmp.name) / 'kanban_equipe.py'), default_timeout=15)
        self.at.session_state['modo_demanda'] = 'editar'
        self.at.session_state['demanda_edit'] = copy.deepcopy(demanda)
        self.at.session_state['itens_temp'] = copy.deepcopy(demanda['itens'])
        self.at.run()
        return demanda

    def campo_data(self):
        campos = [d for d in self.at.date_input if d.label == 'Data da demanda:']
        self.assertEqual(len(campos), 1, 'Editar precisa oferecer Data da demanda')
        return campos[0]

    def test_mudar_data_move_apenas_demanda_selecionada(self):
        todas = copy.deepcopy(self.banco.dados)
        anterior = self.abrir_edicao()
        self.assertEqual(self.campo_data().value, datetime.date.fromisoformat(anterior['data']))
        nova = datetime.date.fromisoformat(anterior['data']) - datetime.timedelta(days=3)
        self.campo_data().set_value(nova).run()
        self.assertEqual(self.banco.gravacoes, [])
        self.botao('✅ Salvar demanda').click().run()
        self.assertEqual(len(self.at.exception), 0)
        esperado = copy.deepcopy(todas)
        esperado[1]['data'] = nova.isoformat()
        self.assertEqual(self.banco.dados, esperado)
        self.assertEqual(len(self.banco.gravacoes), 1)
        self.assertEqual(self.at.session_state['modo_demanda'], 'lista')
        self.assertEqual(self.at.session_state['data_foco'], nova)
        # ID preservado: permanece acessível para editar no novo dia.
        self.assertIn('ed_'+str(anterior['id']), [b.key for b in self.at.button])

    def test_cancelar_alteracao_de_data_nao_grava(self):
        todas = copy.deepcopy(self.banco.dados)
        self.abrir_edicao()
        self.campo_data().set_value(datetime.date.today() + datetime.timedelta(days=5)).run()
        self.botao('❌ Voltar sem salvar').click().run()
        self.assertEqual(self.banco.gravacoes, [])
        self.assertEqual(self.banco.dados, todas)

    def test_data_permanece_ao_adicionar_medida(self):
        self.abrir_edicao()
        nova = datetime.date.today() - datetime.timedelta(days=365)
        self.campo_data().set_value(nova).run()
        self.botao('➕ Adicionar medida').click().run()
        self.assertEqual(self.campo_data().value, nova)
        self.assertEqual(self.banco.gravacoes, [])

    def test_nova_demanda_mantem_data_do_quadro_sem_novo_campo(self):
        self.botao('➕ Nova demanda').click().run()
        self.assertEqual([d for d in self.at.date_input if d.label == 'Data da demanda:'], [])
