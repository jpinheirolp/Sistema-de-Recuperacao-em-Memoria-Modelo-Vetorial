from encodings import utf_8
from enum import unique
from bs4 import BeautifulSoup
from unidecode import unidecode
import pandas as pd
from  math import log
import re
import time
from porter_stemmer import PorterStemmer

ps = PorterStemmer()

def corrige_log_0(num):
    if int(num) == 0:
        return 0.000001
    else:
        return num

arquivo_config = open('BUSCA.CFG', 'r')
config = []
flag_stemmer = False

for linha in arquivo_config:
    if not("=" in linha):
        if linha.replace("\n","").replace(" ","") == "STEMMER": 
    
            flag_stemmer = True
        continue
    linha = linha.split("=")[1]
    linha = linha.replace("<","")
    linha = linha.replace(">","")
    linha = linha.replace("\n","")
    config.append(linha)

arquivo_config.close()

tabela_consultas = pd.read_csv("../RESULT/" + config[1], sep=';', encoding="utf_8")
modelo_vetorial = pd.read_csv("../RESULT/" + config[0], sep=';', encoding="utf_8", index_col=0)
#modelo_vetorial = modelo_vetorial.iloc[:50][:50]
#tabela_consultas = tabela_consultas.iloc[:6][:]
modelo_vetorial.set_index("Words", inplace = True)

nome_arquivo_resultado = config[2]
nome_arquivo, tipo_arquivo = nome_arquivo_resultado.split(".")
nome_arquivo += "-STEMMER" if flag_stemmer else "-NOSTEMMER"
nome_arquivo_resultado = nome_arquivo + "." + tipo_arquivo

arquivo_resultados = open("../RESULT/" + nome_arquivo_resultado, 'w')
texto_arquivo = []

num_docs = len(modelo_vetorial.index) - 1


dic_modulo_docs = modelo_vetorial.T.apply(lambda x: (x**2).sum(), axis=1)

dic_modulo_docs = dic_modulo_docs.to_dict()

dic_dic_vetorial = modelo_vetorial.to_dict("dict")
#print(dic_dic_vetorial.keys())

palavras_consulta = {}
modulo_consulta = 0


for i in tabela_consultas.index:
    id_consulta = tabela_consultas.iloc[i][0]
    texto_consulta = tabela_consultas.iloc[i][1]

    vetor_consulta = re.sub("[^a-zA-Z]+", " ",texto_consulta) 
    vetor_consulta = re.split("['-();:,.!? \n]", vetor_consulta) 
    vetor_consulta_unique = [] 

    for i in range(len(vetor_consulta)):
        palavra_stemmer = vetor_consulta[i].lower()
        palavra_stemmer = ps.stem(palavra_stemmer, 0,len(palavra_stemmer)-1) if flag_stemmer else palavra_stemmer
        palavra_stemmer = palavra_stemmer.upper()
        vetor_consulta[i] = palavra_stemmer

    
    for palavra in vetor_consulta: 

        if not(palavra in modelo_vetorial.index): 
            vetor_consulta  = [i for i in vetor_consulta if i != palavra]
            continue

        if not (palavra in vetor_consulta_unique):
            vetor_consulta_unique.append(palavra) 


    for termo in vetor_consulta_unique:
        
        num_docs_termo = num_docs - modelo_vetorial.loc[termo][:].value_counts().loc[0.0]

        freq_doc = vetor_consulta.count(termo)
        # formula tf/idf

        palavras_consulta[termo] = 1 + log(corrige_log_0(freq_doc)) * log(corrige_log_0( num_docs/num_docs_termo))
        modulo_consulta += palavras_consulta[termo]**2

    
    distancias_documentos = []
    for col in modelo_vetorial.columns:

        if col == "Words":
            continue

        doc_x_consulta = 0

        
        for chave,valor in palavras_consulta.items():
            
            doc_x_consulta += valor*dic_dic_vetorial[col][chave]
    
        
        if dic_modulo_docs[col] == 0:
            continue
        distancia =  doc_x_consulta/(modulo_consulta * dic_modulo_docs[col])
        distancias_documentos.append([col , distancia]) 
   
    
    print(id_consulta)
    distancias_documentos = sorted( distancias_documentos , key=lambda doc: doc[1])
    lista_resultado = []
    for i in range(len(distancias_documentos)):
        lista_resultado.append([i] + ["00"+str(distancias_documentos[i][0])] + [distancias_documentos[i][1]] )
    texto_arquivo.append(str(id_consulta) + ";" + str(lista_resultado) + "\n")

arquivo_resultados.writelines(texto_arquivo)
arquivo_resultados.close()