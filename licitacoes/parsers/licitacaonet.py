#coding: utf8
import re
from datetime import datetime

mail_domain = 'licitacao.net'

class Licitacao:

    site = ''

    def __str__(self):
        return "Numero: %s" % self.numero

class Parser:

    endereco_re = re.compile(u"^Endereço \w+")

    def __init__(self, email):
        iterator = iter(email.read().decode('utf8').splitlines())

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
        licitacao.numero = codigo.split()[1]
        for line in iterator:
            if u"Modalidade" in line:
                licitacao.modalidade = self.extrai_valor(line)
            elif u"Descrição" in line:
                licitacao.objeto = self.extrai_objeto(line, iterator)
            elif u"Licitante" in line:
                licitacao.licitante = self.extrai_licitante(line, iterator)
            elif u"Contato" in line:
                licitacao.contato = self.extrai_valor(line)
            elif u"Data de Entrega" in line:
                lista = line.split()
                licitacao.data_entrega = datetime.strptime(" ".join(lista[3:5]), "%d/%m/%Y %H:%M")
                licitacao.data_abertura = datetime.strptime(" ".join(lista[8:10]), "%d/%m/%Y %H:%M")
            elif self.endereco_re.match(line):
                    licitacao.endereco = line.split(" ", 1)[1]
            elif u"Bairro" in line:
                licitacao.bairro = line.split(" ", 1)[1]
            elif u"Site" in line:
                licitacao.site = line.split(" ", 1)[1].lower()
            elif u"Cidade" in line:
                cidade, uf = line.split(" ", 1)[1].split("-")
                licitacao.cidade = cidade
                licitacao.uf = uf

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

    def __iter__(self):
        return iter(self.licitacoes)

    def next(self):
        return self.licitacoes.next()


if __name__=="__main__":
    f = open("saida.txt", "r")
    for l in Parser(f):
        print l
        print l.licitante
        print l.data_entrega
        print l.data_abertura
        print l.site
        print "======"
    f.close()
