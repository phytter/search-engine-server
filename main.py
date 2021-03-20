from app.routes import add_routes
from app.search_engine import Search_engine
from app import app
import configparser
import argparse
import nltk

if __name__ == '__main__':

    try:
        print('## Baixando pacotes extras...')
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('rslp')
        print('## Pronto...\n')
    except:
        print('## Erro ao baixar os pacotes!\n')
        exit(0)

    print('## Aplicando configurações e instanciando ferramentas...')

    # Caminho da base de dados
    base_dir = '/app/base_de_dados/'
    # Tratamentos a serem aplicados no corpus
    tratement = ['alpha_num', 'lower_case', 'stop_words', 'steamming']


    print('## Instanciando a engine...')
    search_engine = Search_engine(base_dir, tratement)
    print('## Iniciando processamento da base de dados. Isso pode demorar um pouco...')
    search_engine.proccess_database()

    print('## Subindo api...')
    app = app
    add_routes(app, search_engine)
    config = configparser.ConfigParser()
    config.read('config/configuration.cfg')
    app.run(
        host=config.get('general', 'host',fallback='0.0.0.0'),
        port=config.get('general', 'port',fallback='8000'),
        debug=False
    )