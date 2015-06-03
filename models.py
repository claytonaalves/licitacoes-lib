from peewee import *
from peewee import RawQuery

database = MySQLDatabase('licitacoes', **{'user': 'root'})

def formata_data(data):
    dia, mes, ano = data.split('/')
    return "%s-%s-%s" % (ano, mes, dia)

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

    class Meta:
        db_table = 'licitacoes'

    identificacao        = CharField(primary_key = True)
    cidade               = CharField(null = True)
    codigo               = CharField(null = True)
    comprador            = CharField(null = True)
    email                = CharField(null = True)
    endereco             = CharField(null = True)
    modalidade           = CharField(null = True)
    objeto               = TextField(null = True)
    edital               = CharField(max_length=80)
    segmento             = TextField(null = True)
    site                 = CharField(null = True)
    telefone             = CharField(null = True)
    tipo                 = CharField(null = True)
    uf                   = CharField(null = True)
    prazo_credenciamento = DateTimeField(null = True)
    prazo_proposta       = DateTimeField(null = True)
    cotacao_fim          = DateTimeField(null = True)
    cotacao_inicio       = DateTimeField(null = True)
    informacoes          = CharField(null = True)
    arquivo_edital       = CharField(max_length=80)
    valor_estimado       = DecimalField()

    @staticmethod
    def filtrar_por(**kwargs):
        select = Licitacao.select()
        if kwargs['cidade']!='todas':
            select = select.where(Licitacao.cidade==kwargs['cidade'])
        if kwargs['estado']!='todos':
            select = select.where(Licitacao.uf==kwargs['estado'])
        if kwargs['modalidade']!='todas':
            select = select.where(Licitacao.modalidade==kwargs['modalidade'])
        if kwargs['credenciamento_inicio']:
            data1 = formata_data(kwargs['credenciamento_inicio'])+' 00:00:00'
            data2 = formata_data(kwargs['credenciamento_inicio'])+' 23:59:59'
            select = select.where(Licitacao.prazo_credenciamento.between(data1, data2)) 
        if kwargs['credenciamento_fim']:
            data1 = formata_data(kwargs['credenciamento_fim'])+' 00:00:00'
            data2 = formata_data(kwargs['credenciamento_fim'])+' 23:59:59'
            select = select.where(Licitacao.prazo_proposta.between(data1, data2)) 
        if kwargs['cotacao_inicio'] and kwargs['cotacao_fim']:
            select = select.where(
            (Licitacao.cotacao_inicio>=formata_data(kwargs['cotacao_inicio'])+' 00:00:00') &
            (Licitacao.cotacao_fim<=formata_data(kwargs['cotacao_fim'])+' 23:59:59') 
            )
        if kwargs['objeto']:
            select = select.where(SQL("match (objeto) against ('{0}')".format(kwargs['objeto'])))

        select = select.limit(30)
        print select
        return select

