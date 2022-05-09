from encodings import utf_8
from enum import unique
from bs4 import BeautifulSoup
from unidecode import unidecode
import pandas as pd
from  math import log
arquivo_config = open('INDEX.CFG', 'r')
config = []

for linha in arquivo_config:
    linha = linha.split("=")[1]
    linha = linha.replace("<","")
    linha = linha.replace(">","")
    linha = linha.replace("\n","")
    config.append(linha)

arquivo_config.close()

tabela_palavras = pd.read_csv("./robson.csv", sep=';', encoding="utf_8")
tabela_palavras.columns = ["Words",'ListDocs']
num_docs = 0
for row in tabela_palavras.iterrows():
    list_docs = row[1]['ListDocs'].replace("[","")
    list_docs = list_docs.replace("]","")
    list_docs = list_docs.split(",")
    last_doc = int(list_docs[-1])
    num_docs = max(num_docs,last_doc)

tabela_docs = pd.DataFrame(0.0, index=tabela_palavras.index ,columns=range(1,num_docs+1))

tabela_busca = tabela_palavras.join(tabela_docs)
tabela_busca

palavras_indesejadas = []

for i in tabela_busca.index:
    palavra = tabela_busca.iloc[i]['Words']
    if len(str(palavra)) < 2:
        palavras_indesejadas.append(i)

    list_docs = tabela_busca.iloc[i]['ListDocs']
    list_docs = list_docs.replace("[","")
    list_docs = list_docs.replace("]","")
    list_docs = list_docs.split(",")
    list_docs_unique = []
    for d in list_docs:
        if not (d in list_docs_unique):
            list_docs_unique.append(d) 

    num_docs_termo = len(list_docs_unique)
    
    for doc in list_docs_unique:
        freq_doc = list_docs.count(doc)
        # formula tf/idf
        tabela_busca.iat[int(i),int(doc)+1] = 1 + log(freq_doc) * log(num_docs/num_docs_termo)
        
tabela_busca = tabela_busca.drop(palavras_indesejadas,axis=0)
tabela_busca = tabela_busca.drop(['ListDocs'],axis=1)
    
    
print(tabela_busca.iloc[2])
print(tabela_busca.iat[2,778])

tabela_busca.to_csv(config[1], sep=';', encoding='utf-8')
