import bottle
import email.parser
from bottle import route, run, template, request, redirect
from models import *
from licitacoes import parser_factory
from datetime import datetime as dt

bottle.TEMPLATE_PATH.append('www/views')
bottle.debug(True)

def data_filter(data):
    if not data:
        return ''
    return data.strftime("%d/%m/%Y %H:%M:%S")

@route('/', method='GET')
def index():
    return template('index.html', 
                    licitacoes=Licitacao.select().limit(20),
                    cidades=carrega_cidades(),
                    estados=carrega_estados(),
                    modalidades=carrega_modalidades(),
                    formata_data=data_filter)


def formata_data(data):
    dia, mes, ano = data.split('/')
    return "%s-%s-%s" % (ano, mes, dia)

@route('/', method='POST')
def index_with_filter():
    cidade = request.forms.get('cidade')
    estado = request.forms.get('estado')
    modalidade = request.forms.get('modalidade')
    credenciamento_inicio = request.forms.get('credenciamento_inicio')
    credenciamento_fim = request.forms.get('credenciamento_fim')
    cotacao_inicio = request.forms.get('cotacao_inicio')
    cotacao_fim = request.forms.get('cotacao_fim')
    objeto = request.forms.get('objeto')

    selected_items = {
        'cidade': cidade,
        'estado': estado,
        'modalidade': modalidade
    }

    select = Licitacao.select()
    if objeto:
        select = select.where(Licitacao.objeto.contains(objeto))
    if cidade!='todas':
        select = select.where(Licitacao.cidade==cidade)
    if estado!='todos':
        select = select.where(Licitacao.uf==estado)
    if modalidade!='todas':
        select = select.where(Licitacao.modalidade==modalidade)
    if credenciamento_inicio and credenciamento_fim:
        select = select.where(Licitacao.prazo_credenciamento.between(
                                formata_data(credenciamento_inicio), 
                                formata_data(credenciamento_fim)))
    if cotacao_inicio and cotacao_fim:
        select = select.where(Licitacao.cotacao_inicio==formata_data(cotacao_inicio)) 
        select = select.where(Licitacao.cotacao_fim==formata_data(cotacao_fim)) 

    return template('index.html', 
                    licitacoes=select,
                    cidades=carrega_cidades(),
                    estados=carrega_estados(),
                    modalidades=carrega_modalidades(),
                    selected=selected_items,
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
        licitacao.termino_credenciamento = l.termino_credenciamento
        licitacao.termino_envio_proposta = l.termino_envio_proposta
        licitacao.cotacao_inicio = l.cotacao_inicio
        licitacao.cotacao_fim = l.cotacao_fim
        licitacao.save()


    redirect('/')

run(reloader=True)