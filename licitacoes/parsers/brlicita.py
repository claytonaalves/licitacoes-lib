#coding: utf8
import BeautifulSoup as bs
import email.parser
import base64
import re
from datetime import datetime as dt
from ..licitacao import Licitacao

mail_domain = 'brlicita.com.br'

class Parser:

    def __init__(self, email):
        body = base64.decodestring(email.get_payload())

        soup = bs.BeautifulSoup(body.decode('utf8'))

        dados_tabela = soup.find("table", {"id": "dadosTabela"})
        tr = dados_tabela.contents[3]
        table = tr.first().contents[3]
        table2 = table.find("table")
        licitacoes = table2.contents[2:-1]

        self.licitacoes = []

        for html_licitacao in licitacoes:
            if "Alteradas / Retificadas" in html_licitacao.text:
                continue

            licitacao = Licitacao()
            licitacao.tipo = mail_domain
            licitacao.comprador = html_licitacao.find('span').text
            licitacao.uf = html_licitacao.find("span", attrs={"style":"font-weight: 700; font-size: medium;"}).text

            tabela_dados = html_licitacao.findAll("table")[2].findAll("table")[0]
            licitacao.endereco = tabela_dados.find("span").text

            tabela_telefones = tabela_dados.find("table").findAll("tr")
            for item in tabela_telefones:
                if "Telefone" in item.text:
                    licitacao.telefone = item.find("span").text
                elif "Fax" in item.text:
                    licitacao.telefone = item.find("span").text

            links = html_licitacao.findAll("a")
            for link in links:
                if "@" in link.text:
                    licitacao.email = link.text
                else:
                    licitacao.site = link.text

            linha_pregao = html_licitacao.find("table").contents[3]
            licitacao.modalidade = linha_pregao.find("span").text.title()

            endereco = licitacao.endereco.split("-")
            if len(endereco)>2:
                licitacao.cidade = endereco[-1].strip()

            dados_licitacao = html_licitacao.find("table").contents[4:]
            for dado in dados_licitacao:
                tipo = dado.findChild("td")
                tipo_text = tipo.text
                if tipo_text == "Objeto":
                    licitacao.objeto = self.extrai_valor(tipo)
                elif tipo_text == "Segmento":
                    licitacao.segmento = self.extrai_valor(tipo)
                elif tipo_text == u"Abertura":
                    licitacao.cotacao_inicio = dt.strptime(self.extrai_valor(tipo), "%d/%m/%Y %H:%M")
                elif tipo_text == u"Informações":
                    licitacao.informacoes = self.extrai_valor(tipo)
                elif tipo_text == u"Código":
                    licitacao.codigo = self.extrai_valor(tipo)
                elif tipo_text == u"Propostas":
                    inicio, fim = " ".join(self.extrai_valor(tipo).splitlines()).split("a")
                    if not fim:
                        continue 
                    licitacao.termino_envio_proposta = dt.strptime(fim.strip(), "%d/%m/%Y %H:%M")
                elif tipo_text == u"Valor Estimado:":
                    valor = self.extrai_valor(tipo)
                    valor = re.sub("[rR]\$* *", "", valor)
                    valor = valor.replace(".", "")
                    valor = valor.replace(",", ".")
                    licitacao.valor_estimado = float(valor)
                elif tipo_text == u"Edital":
                    licitacao.edital = self.extrai_valor(tipo)
#Edital
#Complementos
#Preço Edital

            self.licitacoes.append(licitacao)

    def extrai_valor(self, tipo):
        valor = tipo.findNextSibling().contents[1]
        valor = "".join(valor.findAll(text=True))
        return valor.strip()

    def __iter__(self):
        return self.licitacoes.__iter__()

    def next(self):
        return self.licitacoes.next()


# ----


    #licitacao.numero = line.split(' ')[1]
    #licitacao.termino_credenciamento = datetime.strptime(data, '%d/%m/%Y %H:%M:%S')
    #licitacao.termino_envio_proposta = datetime.strptime(data, '%d/%m/%Y %H:%M:%S')
    #licitacao.data_cotacao_inicio = datetime.strptime(inicio.strip(), '%d/%m/%Y %H:%M:%S')
    #licitacao.data_cotacao_fim = datetime.strptime(fim.strip(), '%d/%m/%Y %H:%M:%S')

