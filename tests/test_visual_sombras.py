"""Contrato visual; não importa o app nem acessa o banco."""
import ast
from pathlib import Path
import re
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


class VisualSombras(unittest.TestCase):
    def setUp(self):
        tree = ast.parse((ROOT / 'kanban_equipe.py').read_text(encoding='utf8'))
        self.css = next(n.value.args[0].value for n in tree.body if isinstance(n, ast.Expr)
                        and isinstance(n.value, ast.Call) and n.value.args
                        and isinstance(n.value.args[0], ast.Constant)
                        and isinstance(n.value.args[0].value, str) and '<style>' in n.value.args[0].value)

    def regra(self, seletor):
        regras = re.findall(re.escape(seletor) + r'\s*\{([^}]+)', self.css)
        return ' '.join(regras)

    def test_cards_e_indicadores_tem_sombra_propria(self):
        for seletor in ['.metric-card', '[class*="st-key-card_demanda_"]']:
            self.assertIn('box-shadow:', self.regra(seletor), seletor)

    def test_filtros_e_cadastro_sao_destacados(self):
        for seletor in ['.st-key-filtros_producao', '.st-key-cadastro_demanda']:
            self.assertIn('box-shadow:', self.regra(seletor), seletor)

    def test_fundo_tem_contraste_coerente_com_tema(self):
        tema = tomllib.loads((ROOT / '.streamlit/config.toml').read_text(encoding='utf8'))['theme']
        self.assertEqual(tema['backgroundColor'], '#e5ede8')
        self.assertIn('#e5ede8', self.regra('.stApp'))
        self.assertEqual(tema['base'], 'light')


if __name__ == '__main__':
    unittest.main()
