from peewee import *
from peewee import RawQuery

database = MySQLDatabase('licitacoes', **{'user': 'root'})

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

class Cidade(BaseModel):
    nome = CharField(db_column='cidade')

def carrega_cidades():
    return RawQuery(Cidade, 'select distinct cidade from licitacoes order by cidade')

class Estado(BaseModel):
    uf = CharField(db_column='uf')

def carrega_estados():
    return RawQuery(Estado, 'select distinct uf from licitacoes where uf<>"" order by 1')

class Modalidade(BaseModel):
    descricao = CharField(db_column='modalidade')

def carrega_modalidades():
    return RawQuery(Modalidade, 'select distinct modalidade from licitacoes')

class Licitacao(BaseModel):
    identificacao = CharField(primary_key=True)
    cidade = CharField(null=True)
    codigo = CharField(null=True)
    comprador = CharField(null=True)
    cotacao_fim = DateTimeField(null=True)
    cotacao_inicio = DateTimeField(null=True)
    email = CharField(null=True)
    endereco = CharField(null=True)
    informacoes = CharField(null=True)
    modalidade = CharField(null=True)
    objeto = TextField(null=True)
    prazo_credenciamento = DateTimeField(null=True)
    prazo_proposta = DateTimeField(null=True)
    segmento = TextField(null=True)
    site = CharField(null=True)
    telefone = CharField(null=True)
    tipo = CharField(null=True)
    uf = CharField(null=True)

    class Meta:
        db_table = 'licitacoes'

