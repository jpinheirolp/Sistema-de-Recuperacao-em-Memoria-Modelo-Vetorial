from encodings import utf_8
from enum import unique
from bs4 import BeautifulSoup
from unidecode import unidecode
import pandas as pd
from  math import log
import re

arquivo_config = open('BUSCA.CFG', 'r')
config = []

for linha in arquivo_config:
    linha = linha.split("=")[1]
    linha = linha.replace("<","")
    linha = linha.replace(">","")
    linha = linha.replace("\n","")
    config.append(linha)

arquivo_config.close()

tabela_consultas = pd.read_csv(config[1], sep=';', encoding="utf_8")
modelo_vetorial = pd.read_csv(config[0], sep=';', encoding="utf_8")
modelo_vetorial.set_index("Words", inplace = True)

arquivo_resultados = open(config[2], 'w')
texto_arquivo = []

num_docs = len(modelo_vetorial.index) - 1
palavras_consulta = {}
modulo_consulta = 0

print(modelo_vetorial)
print(num_docs)

for i in tabela_consultas.index:
    id_consulta = tabela_consultas.iloc[i][0]
    texto_consulta = tabela_consultas.iloc[i][1]

    vetor_consulta = re.sub("[^a-zA-Z]+", " ",texto_consulta) 
    vetor_consulta = re.split("['-();:,.!? \n]", vetor_consulta) 
    vetor_consulta_unique = [] 

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
        #print("frq",freq_doc)
        #print("num_docstermo",num_docs_termo)
        palavras_consulta[termo] = 1 + log(freq_doc) * log(num_docs/num_docs_termo)
        modulo_consulta += palavras_consulta[termo]**2

    distancias_documentos = []
    for col in modelo_vetorial.columns:
        if col == "Words":
            continue

        modulo_doc = 0
        doc_x_consulta = 0

        for lin in modelo_vetorial.index:
            if pd.isna(lin):
                continue
            
            modulo_doc += (modelo_vetorial.loc[lin][col])**2

        
        for chave,valor in palavras_consulta.items():
            
            doc_x_consulta += valor*modelo_vetorial.loc[chave][col]
        distancia =  doc_x_consulta/(modulo_consulta * modulo_doc)
        distancias_documentos.append([col , distancia]) 
        print("col",col)
    print(distancias_documentos)
    distancias_documentos = sorted( distancias_documentos , key=lambda doc: doc[1])
    lista_resultado = []
    for i in range(len(distancias_documentos)):
        lista_resultado.append([i] + ["00"+str(distancias_documentos[i][0])] + [distancias_documentos[i][1]] )
    texto_arquivo.append(str(id_consulta) + ";" + str(lista_resultado) + "\n")

arquivo_resultados.writelines(texto_arquivo)
arquivo_resultados.close()