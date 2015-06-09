#coding: utf8
import re
from datetime import datetime as dt
from ..licitacao import Licitacao
import base64

mail_domain = 'licitacao.net'

class Parser:

    endereco_re       = re.compile(u"^Endereço \w+")
    email_re          = re.compile(u"^email", flags=re.I)
    site_re           = re.compile(u"^site", flags=re.I)
    datas_re          = re.compile(u"^data de entrega (.+) data de abertura: (.+)", flags=re.I)
    arquivo_edital_re = re.compile(u"^Arquivo Edital")
    inf_adicionais_re = re.compile(u"^Informações Adicionais")
    edital_re         = re.compile(u".+ Edital: (.+)", flags=re.I)

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

    def extrai_valor(self, line):
        return line.split(" ", 1)[1]

    def extrai_licitacao(self, codigo, iterator):
        licitacao = Licitacao()
        licitacao.tipo = mail_domain
        licitacao.codigo = codigo.split()[1]
        for line in iterator:
            if u"Modalidade" in line:
                licitacao.modalidade = self.extrai_valor(line)
                licitacao.modalidade = re.sub('Edital: .+$', '', licitacao.modalidade).strip().title()
            if self.edital_re.match(line):
                licitacao.edital = self.edital_re.match(line).group(1)
            elif u"Descrição" in line:
                licitacao.objeto = self.extrai_objeto(line, iterator)
                licitacao.objeto = re.sub('^\s*descri..o objeto\s*(?i)', '', licitacao.objeto).capitalize()
            elif u"Licitante" in line:
                licitacao.comprador = self.extrai_licitante(line, iterator).title()
            elif u"Contato" in line:
                telefone = self.extrai_valor(line)
                telefone = re.sub("^\s*-", "", telefone).strip()
                telefone = re.sub("\s*-\s*$", "", telefone).strip()
                licitacao.telefone = telefone
            elif self.endereco_re.match(line):
                licitacao.endereco = line.split(" ", 1)[1].title()
            elif self.inf_adicionais_re.match(line):
                licitacao.informacoes = self.extrai_informacoes_adicionais(line, iterator)
            elif self.email_re.match(line):
                lista = line.split()
                if len(lista)>1:
                    licitacao.email = lista[1].lower()
                if len(lista)>3:
                    licitacao.site = lista[3].lower()
            elif u"Bairro" in line:
                licitacao.bairro = line.split(" ", 1)[1]
            elif self.site_re.match(line):
                licitacao.site = line.split(" ", 1)[1].lower()
            elif self.datas_re.match(line):
                entrega, abertura = self.datas_re.match(line).groups()
                licitacao.data_entrega  = dt.strptime(entrega, "%d/%m/%Y %H:%M")
                licitacao.data_abertura = dt.strptime(abertura, "%d/%m/%Y %H:%M")
            elif self.arquivo_edital_re.match(line):
                idr = licitacao.codigo[1:2]
                id = licitacao.codigo[2:]
                licitacao.arquivo_edital = "http://www.licitacao.net/edital.asp?idR={0}&id={1}".format(idr, id)
            elif u"Cidade" in line:
                cidade, uf = line.split(" ", 1)[1].rsplit("-", 1)
                licitacao.cidade = cidade.title()
                licitacao.uf = uf.strip()

            if "voltar ao topo" in line.lower():
                break
        return licitacao
    
    def extrai_objeto(self, line, iterator):
        linhas_descricao = []
        linhas_descricao.append(line.strip())
        for l in iterator:
            if not l:
                break
            linhas_descricao.append(l.strip())
        return " ".join(linhas_descricao)

    def extrai_licitante(self, line, iterator):
        linhas = [line.split(" ", 1)[1].strip()]
        for linha in iterator:
            if not linha:
                break
            linhas.append(linha.strip())
        return " ".join(linhas)

    def extrai_informacoes_adicionais(self, line, iterator):
        try:
            linhas = [line.split(" ", 2)[2].strip()]
        except IndexError:
            return ""
        for linha in iterator:
            if not linha:
                break
            linhas.append(linha.strip())
        return " ".join(linhas).title()


    def __iter__(self):
        return iter(self.licitacoes)

    def next(self):
        return self.licitacoes.next()

