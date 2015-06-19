#coding: utf8
import re
from datetime import datetime as dt
from ..licitacao import Licitacao
import base64

mail_domain = 'licitacao.net'

class Parser:

    def __init__(self, email):
        payload = email.get_payload()[0]
        charset = payload.get_param('charset')
        base64_encoded = payload.get_payload()
        email_body = base64.decodestring(str(base64_encoded))

        iterator = iter(email_body.decode(charset).splitlines())

        self.licitacoes = []
        for line in iterator:
            if u"Código" in line:
                licitacao = self.extrai_licitacao(line, iterator)
                self.licitacoes.append(licitacao)
            if line==u"Súmulas":
                break

    def extrai_licitacao(self, linha, iterator):
        licitacao = Licitacao()
        licitacao.tipo = mail_domain
        licitacao.codigo = linha.split()[1]

        for linha in iterator:
            for padrao, funcao in self.padroes:
                match = padrao.search(linha)
                if match:
                    funcao(self, linha, padrao, iterator, licitacao)

            if "voltar ao topo" in linha.lower():
                break
        return licitacao

    def extrai_valor(self, line):
        return line.split(" ", 1)[1]

    def extrai_objeto(self, linha, regexp, iterator, licitacao):
        linhas_descricao = []
        linhas_descricao.append(linha.strip())
        for l in iterator:
            if not l:
                break
            linhas_descricao.append(l.strip())
        objeto = " ".join(linhas_descricao).capitalize()
        licitacao.objeto = re.sub('^\s*descri..o objeto\s*(?i)', '', objeto)

    def extrai_modalidade_e_edital(self, linha, regexp, iterator, licitacao):
        valor = self.extrai_valor(linha)
        licitacao.modalidade = re.sub('Edital: .+$', '', valor).strip().title()

        match = re.search(u'.+ Edital: (.+)', linha, flags=re.I)
        if match:
            licitacao.edital = match.group(1)

    def extrai_datas(self, linha, regexp, iterator, licitacao):
        entrega, abertura = regexp.match(linha).groups()
        licitacao.data_entrega  = dt.strptime(entrega, "%d/%m/%Y %H:%M")
        licitacao.data_abertura = dt.strptime(abertura, "%d/%m/%Y %H:%M")

    def extrai_comprador(self, linha, regexp, iterator, licitacao):
        linhas = [linha.split(" ", 1)[1].strip()]
        for linha in iterator:
            if not linha:
                break
            linhas.append(linha.strip())
        licitacao.comprador = " ".join(linhas).title()

    def extrai_contato(self, linha, regexp, iterator, licitacao):
        regexp_uasg = re.compile(u'UASG: (\d{5,})', flags=re.I)
        match = regexp_uasg.search(linha)
        if match:
            licitacao.codigo_uasg = match.group(1)
            linha = regexp_uasg.sub('', linha)
        telefone = regexp.sub('', linha)
        telefone = re.sub('^\s*-', '', telefone)
        telefone = re.sub('\s*-\s*$', '', telefone)
        telefone = re.sub('\(0xx\d{2}\)$', '', telefone)
        telefone = re.sub('\s*-\s*$', '', telefone)
        telefone = re.sub('(?i)0xx', '0', telefone)
        licitacao.telefone = telefone.strip()

    def extrai_endereco(self, linha, regexp, iterator, licitacao):
        licitacao.endereco = linha.split(" ", 1)[1].title()

    def extrai_bairro(self, linha, regexp, iterator, licitacao):
        licitacao.bairro = linha.split(" ", 1)[1]

    def extrai_cidade(self, linha, regexp, iterator, licitacao):
        cidade, uf = linha.split(" ", 1)[1].rsplit("-", 1)
        licitacao.cidade = cidade.title()
        licitacao.uf = uf.strip()

    def extrai_email(self, linha, regexp, iterator, licitacao):
        lista = linha.split()
        if len(lista) > 1:
            licitacao.email = lista[1].lower()
        if len(lista) > 3:
            licitacao.site = lista[3].lower()

    def extrai_informacoes_adicionais(self, linha, regexp, iterator, licitacao):
        try:
            linhas = [linha.split(" ", 2)[2].strip()]
        except IndexError:
            return ""
        for linha in iterator:
            if not linha:
                break
            linhas.append(linha.strip())
        licitacao.informacoes = " ".join(linhas).title()

    def extrai_site(self, linha, regexp, iterator, licitacao):
        licitacao.site = linha.split(" ", 1)[1].lower()

    def extrai_arquivo_edital(self, linha, regexp, iterator, licitacao):
        idr = licitacao.codigo[1:2]
        id = licitacao.codigo[2:]
        licitacao.arquivo_edital = "http://www.licitacao.net/edital.asp?idR={0}&id={1}".format(idr, id)

    def __iter__(self):
        return iter(self.licitacoes)

    def next(self):
        return self.licitacoes.next()

    padroes = [
        [re.compile(u'^Descrição', flags=re.I), extrai_objeto],
        [re.compile(u'^Modalidade', flags=re.I), extrai_modalidade_e_edital],
        [re.compile(u'^data de entrega (.+) data de abertura: (.+)', flags=re.I), extrai_datas],
        [re.compile(u'^Licitante', flags=re.I), extrai_comprador],
        [re.compile(u'^Contato', flags=re.I), extrai_contato],
        [re.compile(u"^Endereço \w+"), extrai_endereco],
        [re.compile(u"^Bairro \w+"), extrai_bairro],
        [re.compile(u"^Cidade \w+"), extrai_cidade],
        [re.compile(u"^email", flags=re.I), extrai_email],
        [re.compile(u"^Informações Adicionais"), extrai_informacoes_adicionais],
        [re.compile(u"^site", flags=re.I), extrai_site],
        [re.compile(u'^Arquivo Edital'), extrai_arquivo_edital],
    ]

