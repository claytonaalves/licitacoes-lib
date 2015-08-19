import bottle
import email.parser
from bottle import route, run, template, request, redirect, auth_basic
from models import *
from licitacoes import parser_factory
from datetime import datetime as dt

bottle.TEMPLATE_PATH.append('www/views')
bottle.debug(True)

def data_filter(data):
    if not data:
        return ''
    return data.strftime("%d/%m/%Y %H:%M:%S")

def authenticate_user(username, password):
    return (username=='teste' and password=='1234')


@route('/', method='GET')
@auth_basic(authenticate_user)
def index():
    return template('index.html', 
                    licitacoes=Licitacao.select().limit(20),
                    cidades=carrega_cidades(),
                    estados=carrega_estados(),
                    modalidades=carrega_modalidades(),
                    formata_data=data_filter)

@route('/css/<filename>')
def css_files(filename):
    return bottle.static_file(filename, root='www/css')

@route('/', method='POST')
def index_with_filter():
    select = Licitacao.filtrar_por(
        cidade           = request.forms.get('cidade'),
        estado           = request.forms.get('estado'),
        modalidade       = request.forms.get('modalidade'),
        data_entrega     = request.forms.get('data_entrega'),
        data_abertura    = request.forms.get('data_abertura'),
        termino_proposta = request.forms.get('termino_proposta'),
        cotacao_fim      = request.forms.get('cotacao_fim'),
        objeto           = request.forms.get('objeto')
    )

    filter_options = {
        'cidade': request.forms.get('cidade').decode('utf8'),
        'estado': request.forms.get('estado'),
        'modalidade': request.forms.get('modalidade').decode('utf8'),
        'objeto': request.forms.get('objeto').decode('utf8')
    }

    return template('index.html', 
                    licitacoes=select,
                    cidades=carrega_cidades(),
                    estados=carrega_estados(),
                    modalidades=carrega_modalidades(),
                    selected=filter_options,
                    formata_data=data_filter)


@route('/enviar', method='GET')
def enviar():
    return template('enviar.html')

@route('/upload', method='POST')
def do_upload():
    upload = request.files.get('upload')

    email_parser = email.parser.Parser()
    parsed_email = email_parser.parse(upload.file)
    licitacoes = parser_factory(parsed_email)

    for l in licitacoes:
        q = Licitacao.delete().where(Licitacao.identificacao==l.identificacao)
        q.execute()

        licitacao = Licitacao.create(identificacao = l.identificacao)
        licitacao.codigo = l.codigo
        licitacao.tipo = l.tipo
        licitacao.comprador = l.comprador
        licitacao.endereco = l.endereco
        licitacao.objeto = l.objeto
        licitacao.cidade = l.cidade
        licitacao.uf = l.uf
        licitacao.telefone = l.telefone
        licitacao.email = l.email
        licitacao.site = l.site
        licitacao.modalidade = l.modalidade
        licitacao.informacoes = l.informacoes
        licitacao.segmento = l.segmento
        licitacao.data_entrega = l.data_entrega
        licitacao.data_abertura = l.data_abertura
        licitacao.termino_proposta = l.termino_proposta
        licitacao.cotacao_fim = l.cotacao_fim
        licitacao.valor_estimado = l.valor_estimado
        licitacao.edital = l.edital
        licitacao.arquivo_edital = l.arquivo_edital
        licitacao.codigo_uasg = l.codigo_uasg
        licitacao.save()

    redirect('/')

run(reloader=True)

