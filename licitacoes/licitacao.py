#coding: utf8
import hashlib

class Licitacao:
    comprador              = None # Licitante
    endereco               = u'Não informado'
    uf                     = ''
    telefone               = u'Não informado'
    email                  = u'Não informado'
    site                   = u'Não informado'
    cidade                 = u'Não informado'
    tipo                   = u'Não informado' 

    codigo                 = ''
    edital                 = ''
    segmento               = ''
    modalidade             = None
    objeto                 = None

    prazo_credenciamento   = None
    prazo_proposta         = None

    cotacao_inicio         = None
    cotacao_fim            = None

    informacoes            = ''
    arquivo_edital         = ''

    valor_estimado         = 0
    
    @property
    def identificacao(self):
        sha1 = hashlib.sha1()
        sha1.update(self.comprador.encode('utf8'))
        sha1.update(self.codigo)
        sha1.update(self.tipo)
        return sha1.hexdigest()


