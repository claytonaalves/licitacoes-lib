#!/usr/bin/env python

import os
import argparse

from bottle import run


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', dest='db', choices=['mysql', 'sqlite'],
                        default='mysql')
    args = parser.parse_args()
    os.environ.setdefault('LICITACOES_DB', args.db)

    from app import app
    run(app, reloader=True)
