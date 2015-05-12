#coding: utf8
import re
from datetime import datetime
from ..licitacao import Licitacao

mail_domain = 'caixa.gov.br'

def extrai_valor(line):
    lista = line.split(':', 1)

    if len(lista)>1:
        valor = lista[1].strip()
    else:
        valor = lista[0].strip()

    return valor

def extrai_data(line):
    data_texto = extrai_valor(line)
    try:
        data = datetime.strptime(data_texto, '%d/%m/%Y')
    except ValueError:
        data = datetime.now()
    return data

def extrai_data_hora(line):
    data_texto = extrai_valor(line)
    try:
        data = datetime.strptime(data_texto, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        data = extrai_data(line)
    return data

class Parser:

    intervalo_re = re.compile(u"Intervalo de cotação:* (.+) a (.+)", flags=re.I)
    codigo_re = re.compile(u"^\s*N. ")

    def __init__(self, email):
        lines = email.get_payload().splitlines()

        self.licitacoes = []

        licitacao = None
        for line in lines:
            if 'Comprador' in line:
                licitacao = Licitacao()
                licitacao.tipo = 'caixa.gov.br'
                self.licitacoes.append(licitacao)
            self.processa_linha(line.decode('latin1').strip(), licitacao)

    def processa_linha(self, line, licitacao):
        if 'Comprador' in line:
            licitacao.comprador = line.split(':')[1].strip()
            lista = licitacao.comprador.split('/')
            if len(lista)>1:
                licitacao.uf = lista[1].strip()
                licitacao.comprador = lista[0]
            m = re.search('prefeitura \w+ de (.+)', licitacao.comprador, flags=re.I)
            if m:
                licitacao.cidade = m.groups()[0].strip()
        if 'Modalidade' in line:
            licitacao.modalidade = line.split(':')[1].strip()
        if 'Objeto' in line:
            licitacao.objeto = line.split(':')[1].strip()
        if self.codigo_re.match(line):
            licitacao.codigo = line.split(' ')[1]
        if u'Término do Credenciamento' in line:
            licitacao.termino_credenciamento = extrai_data_hora(line)
        if u'Término do Envio de Proposta' in line:
            licitacao.termino_envio_proposta = extrai_data_hora(line)
        if self.intervalo_re.match(line):
            inicio, fim = self.intervalo_re.match(line).groups()
            licitacao.cotacao_inicio = datetime.strptime(inicio.strip(), '%d/%m/%Y %H:%M:%S')
            licitacao.cotacao_fim = datetime.strptime(fim.strip(), '%d/%m/%Y %H:%M:%S')

    def __iter__(self):
        return self.licitacoes.__iter__()

    def next(self):
        return self.licitacoes.next()
        
        

