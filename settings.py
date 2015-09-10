
import os

from peewee import MySQLDatabase, SqliteDatabase

db = os.environ.get('LICITACOES_DB')

if db == 'mysql':
    database = MySQLDatabase('licitacoes', **{'user': 'root'})
elif db == 'sqlite':
    database = SqliteDatabase('licitacoes.db', threadlocals=True)
