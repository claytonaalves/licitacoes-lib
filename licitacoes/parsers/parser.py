#coding: utf8
from . import brlicita
from . import caixa
from . import licitacaonet

parsers = [brlicita, caixa, licitacaonet]

def parser_factory(parsed_email):
    """ Retorna um iterator de acordo com o domínio do email
    """
    mail_from = parsed_email.get('from')
    parser = None
    for parser_module in parsers:
        if parser_module.mail_domain in mail_from:
            parser = parser_module.Parser(parsed_email)
    return parser

