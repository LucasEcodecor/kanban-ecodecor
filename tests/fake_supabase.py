"""Somente testes: banco em memória, sem credenciais, rede ou dados da empresa."""
import copy
import datetime
from types import ModuleType, SimpleNamespace


ETAPAS = ['ETIQUETAS (LUCAS)', 'ARTE (CAIO/LUCAS)', 'IMPRESSÃO (CAIO)',
          'CORTE EM ANDAMENTO (CASSIO)', 'CORTE FINALIZADO (CASSIO)',
          'PRODUÇÃO EM ANDAMENTO (GUSTAVO)', 'PRODUÇÃO FINALIZADO (GUSTAVO)',
          'NOTA FISCAL (MICHELLI)', 'LIBERADO PARA ENTREGA (MICHELLI)']


def dados_exemplo():
    dia = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    return [dict(id=i, cliente=f'CLIENTE FICTÍCIO {i:02}', nf=f'TESTE{i:03}', data=dia,
                 ordem=i, itens=[{'tam': '30x40', 'qtd': 86}], referencia='AMOSTRA',
                 agendamento='', etapas=({} if i % 3 == 1 else
                    dict.fromkeys(ETAPAS, True) if i % 3 == 0 else {ETAPAS[0]: True}))
            for i in range(1, 22)]


class BancoFake:
    def __init__(self):
        self.dados = dados_exemplo()
        self.gravacoes = []
    def table(self, nome):
        assert nome == 'demandas'
        return Consulta(self)


class Consulta:
    def __init__(self, banco):
        self.banco = banco
        self.filtros = []
        self.acao = 'select'
        self.payload = None
        self.limite = None
    def select(self, *args):
        return self
    def eq(self, campo, valor):
        self.filtros.append(lambda d: d.get(campo) == valor)
        return self
    def ilike(self, campo, valor):
        self.filtros.append(lambda d: str(valor).strip('%').lower() in str(d.get(campo, '')).lower())
        return self
    def order(self, *args, **kwargs):
        return self
    def limit(self, valor):
        self.limite = valor
        return self
    def update(self, payload):
        self.acao, self.payload = 'update', payload
        return self
    def insert(self, payload):
        self.acao, self.payload = 'insert', payload
        return self
    def delete(self):
        self.acao = 'delete'
        return self
    def execute(self):
        linhas = [d for d in self.banco.dados if all(f(d) for f in self.filtros)]
        if self.acao == 'select':
            return SimpleNamespace(data=copy.deepcopy(linhas[:self.limite]))
        self.banco.gravacoes.append((self.acao, copy.deepcopy(self.payload)))
        if self.acao == 'update':
            for d in linhas:
                d.update(copy.deepcopy(self.payload))
        elif self.acao == 'insert':
            self.banco.dados.append(dict(copy.deepcopy(self.payload), id=1000))
        elif self.acao == 'delete':
            self.banco.dados = [d for d in self.banco.dados if d not in linhas]
        return SimpleNamespace(data=copy.deepcopy(linhas))


def modulo_fake(banco):
    modulo = ModuleType('supabase')
    modulo.Client = BancoFake
    modulo.create_client = lambda *args, **kwargs: banco
    return modulo
