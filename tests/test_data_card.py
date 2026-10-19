"""Callbacks reais sem rede; abertura/fechamento conferidos no navegador.

AppTest 1.56 não preserva o estado do popover entre interações. Testamos
persistência com as funções reais e conferimos o popover no navegador.
"""
import copy
import datetime
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from fake_supabase import BancoFake, Consulta
from test_regras_interface import carregar_funcoes


class Estado(dict):
    def __setattr__(self, nome, valor):
        self[nome] = valor


class DataCard(unittest.TestCase):
    def setUp(self):
        self.banco = BancoFake()
        self.antes = copy.deepcopy(self.banco.dados)
        self.foco = datetime.date.fromisoformat(self.antes[1]['data'])
        self.nova = self.foco + datetime.timedelta(days=2)
        self.estado = Estado(data_card_2=self.nova, popover_data_2=True,
                             data_foco=self.foco, pagina_atual=2, modo_demanda='lista')
        self.ns = carregar_funcoes()
        self.limpezas = []
        self.ns.update(st=SimpleNamespace(session_state=self.estado), supabase=self.banco,
                       limpar_cache=lambda: self.limpezas.append(True))

    def test_salvar_data_no_card_preserva_todos_demais_campos(self):
        self.ns['salvar_data_card'](2)
        esperado = copy.deepcopy(self.antes)
        esperado[1]['data'] = self.nova.isoformat()
        self.assertEqual(self.banco.dados, esperado)
        self.assertEqual(self.banco.gravacoes, [('update', {'data': self.nova.isoformat()})])
        self.assertEqual(self.estado['data_foco'], self.nova)
        self.assertEqual(self.estado['pagina_atual'], 1)
        self.assertEqual(self.estado['modo_demanda'], 'lista')
        self.assertFalse(self.estado['popover_data_2'])
        self.assertEqual(self.limpezas, [True])

    def test_cancelar_restaura_data_sem_gravacao(self):
        self.estado['erro_data_card_2'] = 'Erro anterior'
        self.ns['cancelar_data_card'](2)
        self.assertEqual(self.banco.gravacoes, [])
        self.assertEqual(self.banco.dados, self.antes)
        self.assertEqual(self.estado['data_foco'], self.foco)
        self.assertNotIn('data_card_2', self.estado)
        self.assertFalse(self.estado['popover_data_2'])
        self.assertNotIn('erro_data_card_2', self.estado)

    def test_falha_na_gravacao_mantem_data_original(self):
        with patch.object(Consulta, 'execute', side_effect=RuntimeError('Falha simulada de conexão')):
            self.ns['salvar_data_card'](2)
        self.assertEqual(self.banco.dados, self.antes)
        self.assertEqual(self.banco.gravacoes, [])
        self.assertEqual(self.estado['data_foco'], self.foco)
        self.assertTrue(self.estado['popover_data_2'])
        self.assertIn('Erro ao alterar a data', self.estado['erro_data_card_2'])
        self.assertEqual(self.limpezas, [])

    def test_data_vazia_nao_grava(self):
        self.estado['data_card_2'] = None
        self.ns['salvar_data_card'](2)
        self.assertEqual(self.banco.gravacoes, [])
        self.assertEqual(self.estado['data_foco'], self.foco)
        self.assertIn('Escolha uma data', self.estado['erro_data_card_2'])
