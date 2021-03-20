import nltk
import glob
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.probability import FreqDist
from nltk.stem import RSLPStemmer
import math
import pandas as pd
import argparse
import sys
import seaborn as sns; sns.set_theme()
import json

class Search_engine:

  def __init__(self, dataset_dir, methods):
    if dataset_dir is None:
      raise Exception('É necessário passar o caminho para a base de dados.')
    
    files_path = glob.glob(dataset_dir + '**/*.txt', recursive=True)

    if len(files_path) == 0:
      raise Exception('Nenhum arquivo válido foi encontrado no caminho especificado.')

    # steammer
    self.stemmer = RSLPStemmer()
    # Configurando stop words para poturgues
    self.stopwords = set(nltk.corpus.stopwords.words('portuguese'))
    # Definindo detector de sentenças
    self.sentence_detector = nltk.data.load('tokenizers/punkt/portuguese.pickle')

    self.dataset_dir = dataset_dir
    self.__files_path = files_path
    self.methods_to_treatment = methods
    self.__matriz = {}
    self.__matriz_freq_doc = {}
    self.someError = False
    self.loaded_from_disk = False
    try:
      last_matriz_tf = open("/app/app/last_matriz_tf-idf.json", "r")
      self.__matriz = json.load(last_matriz_tf)
      freq_word_doc_file = open("/app/app/last_matriz_freq_word_doc.json", "r")
      self.__matriz_freq_doc = json.load(freq_word_doc_file)
      self.loaded_from_disk = True
    except:
      pass

  def __get_file_name(self, path):
    if not path:
      return ''
    name = path.split('/')[-1].split('.')[0]
    return name

  def __merge_single_string(self, document):
    if document is None: return ''
    text = ''
    for l in document:
      text += ' ' + l
    return text

  ## Removendo duplicados, mas mantendo a ordem e otimizado (https://www.peterbe.com/plog/uniqifiers-benchmark)
  def __rem_dup(self, seq, idfun=None): 
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

  def __pre_proccessing(self, tokens_to_proccess, methods = []):
    tokens = tokens_to_proccess
    for method in methods:
      # Mantain only alphanum 
      if method == 'alpha_num':
        tokens = [t for t in tokens if t.isalnum()]
      
      # All tokens to lower case
      if method == 'lower_case':
        tokens = [t.lower() for t in tokens]
      
      # removing the stop words
      if method == 'stop_words':
        tokens = [w for w in tokens if w not in self.stopwords]

      # byby words duplicated
      if method == 'remove_duplicated':
        tokens = self.__rem_dup(tokens)

      # steaming
      if method == 'steamming':
        tokens = [self.stemmer.stem(t) for t in tokens]
        # tokens = __rem_dup(tokens)

    return tokens

  def proccess_database(self):
    if self.loaded_from_disk:
      return
    matriz = {}
    freq_word_doc = []

    # Calcula a frequência dos termos nos documentos
    for idx, file in enumerate(self.__files_path):
      # leitura 
      document = open(file, 'r', encoding='latin1')
      # String única com todo o conteúdo
      text_document = self.__merge_single_string(document)
      # Nome do documento
      name_file = self.__get_file_name(file)
      # text_document += ' ' + name_file
      # usando sent_tokenize
      sentences_proccessed = sent_tokenize(text_document.replace('\n', ' '))
      # tokenization
      tokens = []
      for s in sentences_proccessed:
          words = word_tokenize(s)    
          tokens.extend(words)
      # normalizacao
      tokens_normalized = self.__pre_proccessing(tokens, ['alpha_num', 'lower_case', 'stop_words', 'remove_duplicated', 'steamming', 'remove_duplicated'])
      freq_word_doc.extend(tokens_normalized)
    freq_word_doc = FreqDist(freq_word_doc)
    self.__matriz_freq_doc = freq_word_doc
    # matriz de pesos tf-idf
    for idx, file in enumerate(self.__files_path):
      document = open(file, 'r', encoding='latin1')
      text_document = self.__merge_single_string(document)
      name_file = self.__get_file_name(file)
      # text_document += ' ' + name_file
      # usando sent_tokenize
      sentences_proccessed = sent_tokenize(text_document.replace('\n', ' '))
      # tokenization
      tokens = []
      for s in sentences_proccessed:
          words = word_tokenize(s)    
          tokens.extend(words)
      # normalizacao
      tokens_normalized = self.__pre_proccessing(tokens, self.methods_to_treatment)
      # freq dos termos no documento
      freq_tokens = FreqDist(tokens_normalized)
      # qtd de documentos
      qtd_doc = len(self.__files_path)
    
      # Acrescentar na matrix essas freq
      for token in freq_tokens:
        try:
          num = (qtd_doc - freq_word_doc[token] * 0.5) 
          idf =  math.log10( num / freq_word_doc[token] )
          if idf <= 0:
            idf = 0.01
        except:
          idf =  0.01

        try:
          tf_idf = { 'value': (1.0 + math.log10( freq_tokens[token] )) * idf, 'doc': name_file }
          matriz[token][idx] = tf_idf
        except KeyError:
          matriz[token] = [{'value': 0, 'doc': ''}] * qtd_doc
          tf_idf = { 'value': (1.0 + math.log10( freq_tokens[token] )) * idf, 'doc': name_file }
          matriz[token][idx] = tf_idf

    self.__matriz = matriz


  def search_ranked(self, search):
    search_tokens = search.split(' ')
    search_tokens = self.__pre_proccessing(search_tokens, ['alpha_num', 'lower_case', 'stop_words', 'steamming'])
    tfidf_search = self.__calculate_idf_search(
      self.__pre_proccessing(search.split(' '),
      ['alpha_num', 'lower_case', 'stop_words', 'steamming'],
    ))

    files_name = [ self.__get_file_name(file) for file in self.__files_path]
    dict_rank = {}
    common_tokens_mat = []
    # recupero da matriz os termos em comuns com a consulta
    for i in search_tokens:
      try:
        common_tokens_mat.append(self.__matriz[i])
      except:
        pass

    if len(common_tokens_mat) == 0:
      print('Nenhum resultado foi encontrado para a sua busca!\n')
      return

    for i_doc, file_name in enumerate(files_name):
      doc_vector = [doc[i_doc]['value'] for doc in common_tokens_mat ]
      doc_vector_normalized = self.__normalize(doc_vector)
      cos = 0
      for idx, i in enumerate(search_tokens):
        try:
          cos += doc_vector_normalized[idx] * tfidf_search[i]
        except:
          pass
      dict_rank[file_name] = cos

    list_rank = [(k, v) for k, v in dict_rank.items()] 
    results = sorted(list_rank, key = lambda i: i[1], reverse=True)

    return results
    # print('Mostrando os 10 primeiros do ranking\n')
    # for result in results:
    #   print(f'{result[0]} - {result[1]}')
    # print('\n')

  def __normalize(self, vector):
    acc = 0
    for v in vector:
      acc += v ** 2
    norm = math.sqrt(acc)
    aux_vector = []
    for v in vector:
      if norm:
        aux_vector.append(v / norm)
      else:
        aux_vector.append(0)
    return aux_vector

  def __calculate_idf_search(self, search):
    freq_tokens = FreqDist(search)
    tfidf = {}
    qtd_doc = len(self.__files_path)
    for token in freq_tokens:
      try:
        idf =  math.log10( qtd_doc / self.__matriz_freq_doc[token] )
        if idf <= 0:
          idf = 0.01
      except:
        idf =  0.01

      tfidf[token] = (1 + math.log10( freq_tokens[token] )) * idf
    normalized = self.__normalize([ v for k, v in tfidf.items() ])

    for idx, token in enumerate(freq_tokens):
      tfidf[token] = normalized[idx]

    return tfidf


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("-p", "--path", help="-p para especificar o caminho")
  args = parser.parse_args()

  if args.path is None:
    raise Exception('É necessário passar o caminho para a base de dados.')
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
  base_dir = args.path
  # Tratamentos a serem aplicados no corpus
  tratement = ['alpha_num', 'lower_case', 'stop_words', 'steamming']


  print('## Instanciando a engine...')
  search_engine = Search_engine(base_dir, tratement)
  print('## Iniciando processamento da base de dados. Isso pode demorar um pouco...')
  search_engine.proccess_database()
  search = input('Busca: ')
  while search != 'exit':
    search_engine.search_ranked(search)
    search = input('Busca: ')
