#coding: utf8
import re
from datetime import datetime
from ..licitacao import Licitacao

mail_domain = 'caixa.gov.br'

class Parser:

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
        if u'Nº' in line:
            licitacao.numero = line.split(' ')[1]
        if u'Término do Credenciamento' in line:
            data = line.split(':', 1)[1].strip()
            licitacao.termino_credenciamento = datetime.strptime(data, '%d/%m/%Y %H:%M:%S')
        if u'Término do Envio de Proposta' in line:
            data = line.split(':', 1)[1].strip()
            licitacao.termino_envio_proposta = datetime.strptime(data, '%d/%m/%Y %H:%M:%S')
        if u'Intervalo de Cotação' in line:
            datas = line.split(':', 1)[1]
            inicio, fim = datas.split('a')
            licitacao.data_cotacao_inicio = datetime.strptime(inicio.strip(), '%d/%m/%Y %H:%M:%S')
            licitacao.data_cotacao_fim = datetime.strptime(fim.strip(), '%d/%m/%Y %H:%M:%S')

    def __iter__(self):
        return self.licitacoes.__iter__()

    def next(self):
        return self.licitacoes.next()
        
        

