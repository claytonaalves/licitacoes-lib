#coding: utf8
import re
from datetime import datetime
from ..licitacao import Licitacao
from itertools import chain
import base64

mail_domain = 'planejamento.gov.br'

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

    def __init__(self, email):
        base64_encoded = email.get_payload()
        email_body = base64.decodestring(str(base64_encoded))
        iterator = iter(email_body.splitlines())
        self.licitacoes = []

        for line in iterator:
            if u"ORGÃO:" in line.decode('utf8'):
                licitacao = self.extrai_licitacao(line, iterator)
                self.licitacoes.append(licitacao)

    def extrai_licitacao(self, linha, iterator):
        licitacao = Licitacao()
        licitacao.tipo = 'ComprasNet'

        for line in chain([linha], iterator):
            for padrao, funcao in self.padroes:
                match = padrao.search(line.decode('utf8'))
                if match:
                    funcao(self, line, match, iterator, licitacao)

            if line.startswith('****'):
                break
        return licitacao

    # ORGÃO = comprador
    # Código da UASG = contato
    def extrai_comprador(self, line, match, iterator, licitacao):
        linhas = [match.group(1)]
        for line in iterator:
            if not line.strip():
                break
            if 'UASG' in line:
                licitacao.codigo_uasg = line.split(':')[1].strip()
                continue
            else:
                linhas.append(line.decode('utf8').strip())
        licitacao.comprador = u', '.join(linhas)

    # Pregao Eletronico = modalidade
    # Num. Edital
    def extrai_linha_modalidade(self, line, match, iterator, licitacao):
        licitacao.modalidade = match.group(0)
        match = re.search('N. (\d+/\d+)', line.decode('utf8'))
        if match:
            licitacao.edital = match.group(1)

    # OBJETO = OBJETO
    def extrai_objeto(self, line, match, iterator, licitacao):
        licitacao.objeto = re.sub('objeto:(?i)', '', line).strip()
        licitacao.objeto = re.sub('pregão eletrônico\s*-\s*(?i)', '', licitacao.objeto)

    # ENTREGA DA PROPOSTA = Data da Abertura
    def extrai_data_abertura(self, line, match, iterator, licitacao):
        data = re.sub('[a-zA-Z.,]', '', line).strip()
        data = re.sub('^:\s*', '', data)
        data = re.sub('\s*:$', '', data)
        licitacao.data_abertura = datetime.strptime(data, '%d/%m/%Y à %H:%M:%S')

    # ABERTURA DA PROPOSTA = Data da Entrega
    def extrai_data_entrega(self, line, match, iterator, licitacao):
        data = line.split(',')[0]
        data = re.sub('[a-zA-Z.,]', '', data).strip()
        data = re.sub('^:\s*', '', data)
        data = re.sub('\s*:$', '', data)
        licitacao.data_entrega = datetime.strptime(data, '%d/%m/%Y à %H:%M:%S')

    def extrai_informacoes_adicionais(self, line, match, iterator, licitacao):
        informacoes = []
        iterator.next()
        for line in iterator:
            if not line:
                break
            informacoes.append(line.strip())
        licitacao.informacoes = ', '.join(informacoes)

    def __iter__(self):
        return self.licitacoes.__iter__()

    def next(self):
        return self.licitacoes.next()
        
    padroes = [
        [re.compile(u"^\s*ORGÃO: (.+)$", flags=re.I), extrai_comprador],
        [re.compile(u"^(Pregão Eletrônico|Convite)", flags=re.I), extrai_linha_modalidade],
        [re.compile(u"^OBJETO:", flags=re.I), extrai_objeto],
        [re.compile(u"^ENTREGA DA PROPOSTA:", flags=re.I), extrai_data_entrega],
        [re.compile(u"^ABERTURA DA PROPOSTA:", flags=re.I), extrai_data_abertura],
        [re.compile(u"^SERVIÇOS:", flags=re.I), extrai_informacoes_adicionais],
        [re.compile(u"^MATERIAIS:", flags=re.I), extrai_informacoes_adicionais],
    ]

