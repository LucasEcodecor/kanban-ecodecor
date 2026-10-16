"""Extrai apenas funções puras: não inicia o app e não conecta ao Supabase."""
import ast
import datetime
import html
import math
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def carregar_funcoes():
    arvore = ast.parse((ROOT / 'kanban_equipe.py').read_text(encoding='utf-8'))
    nomes = {'CLIENTE_BIGODINHO', 'ETAPAS_PRODUCAO', 'ETAPAS_COMPATIBILIDADE'}
    nodes = [n for n in arvore.body if isinstance(n, ast.FunctionDef) and not n.decorator_list]
    nodes += [n for n in arvore.body if isinstance(n, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id in nomes for t in n.targets)]
    namespace = dict(datetime=datetime, math=math, re=re, escape=html.escape)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<funcoes-isoladas>', 'exec'), namespace)
    return namespace


class PainelFake:
    def __init__(self):
        self.aberturas = []
    def expander(self, label, **kwargs):
        self.aberturas.append(kwargs.get('expanded'))
        return self
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def columns(self, n):
        return [self] * n
    def __getattr__(self, nome):
        return lambda *args, **kwargs: None


class RegrasInterface(unittest.TestCase):
    def setUp(self):
        self.ns = carregar_funcoes()

    def test_notificacoes_nao_abrem_automaticamente(self):
        painel = PainelFake()
        self.ns['st'] = painel
        alerta = {'titulo': 'Nova demanda', 'texto': 'Teste', 'data': '2026-10-16'}
        self.ns['mostrar_painel_alertas']([alerta])
        self.ns['mostrar_painel_alertas']([alerta, alerta])
        self.ns['mostrar_painel_alertas']([])
        self.assertEqual(painel.aberturas, [False, False, False])

    def test_filtro_situacao_etapa_e_compatibilidade_sem_mutacao(self):
        self.assertTrue('filtrar_por_producao' in self.ns, 'Falta filtro de produção')
        etapas = self.ns['ETAPAS_PRODUCAO']
        dados = [
            {'id': 1, 'etapas': {}},
            {'id': 2, 'etapas': {'CORTE EM ANDAMENTO (DAVID)': True}},
            {'id': 3, 'etapas': dict.fromkeys(etapas, True)},
        ]
        filtrar = self.ns['filtrar_por_producao']
        self.assertEqual([d['id'] for d in filtrar(dados, 'Pendentes', 'Todas')], [1])
        self.assertEqual([d['id'] for d in filtrar(dados, 'Em andamento', 'Todas')], [2])
        self.assertEqual([d['id'] for d in filtrar(dados, 'Finalizadas', 'Todas')], [3])
        self.assertEqual([d['id'] for d in filtrar(dados, 'Todas', etapas[3])], [2, 3])
        self.assertEqual(filtrar([], 'Todas', 'Todas'), [])
        self.assertEqual(len(dados), 3)
        self.assertEqual(dados[1]['etapas'], {'CORTE EM ANDAMENTO (DAVID)': True})

    def test_capacidades_e_etiquetas_preservadas(self):
        cap = self.ns['obter_capacidade']
        self.assertEqual(cap('CLIENTE TESTE', '30x40'), 43)
        self.assertEqual(cap('CLIENTE TESTE', '60x40'), 22)
        self.assertEqual(cap('GALPAO DROP LTDA (BIGODINHO)', '80x50'), 10)
        self.assertEqual(cap('CLIENTE TESTE', '80x50'), 11)
        demanda = {'nf': 'TESTE', 'cliente': 'BIGODINHO', 'itens': [{'tam': '80x50', 'qtd': 20}]}
        texto = self.ns['gerar_txt_etiquetas']([demanda])
        self.assertIn('GALPAO DROP LTDA (BIGODINHO)', texto)
        self.assertIn('QUANTIDADE: 10 unidades', texto)
        self.assertEqual(self.ns['total_caixas']([demanda]), 2)


if __name__ == '__main__':
    unittest.main()
