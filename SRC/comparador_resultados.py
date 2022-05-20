from bs4 import BeautifulSoup
from unidecode import unidecode
import math
import matplotlib.pyplot as plt
import pandas as pd

arquivo_config = open('CR.CFG', 'r')
config = []

for linha in arquivo_config:
    linha = linha.split("=")[1]
    linha = linha.replace("<","")
    linha = linha.replace(">","")
    linha = linha.replace("\n","")
    config.append(linha)

arquivo_config.close()

#print(config)

arquivo_esperado = open('../RESULT/'+config[0],'r') 

dic_esperados = dict()

for linha in arquivo_esperado:
    linha = linha.replace("\n","").replace(" ","")
    consulta,doc,votos = linha.split(";")
    if not(consulta.isdecimal()):
        continue

    consulta = str(int(consulta))
    if not(consulta in dic_esperados.keys()):
        dic_interno = dict()
        dic_interno[doc] = votos
        dic_esperados[consulta] = dic_interno
        continue
    
    dic_esperados[consulta][doc] = votos   
    
arquivo_esperado.close()

dic_resultados = dict()

arquivo_resultados = open('../RESULT/'+config[1],'r')
for linha in arquivo_resultados:
    linha = linha.replace("\n","").replace(" ","")
    consulta,lista_resultados = linha.split(";")
    #print(lista_resultados)
    lista_resultados = lista_resultados[1:-1].split('[')
    lista_doc = []
    for lista_rank in lista_resultados:
        doc = lista_rank.strip("],").split(",")
        if len(doc) < 3: continue
        doc = doc[1]
        doc = doc.strip("'")
        doc = str(int(doc))
        lista_doc.append(doc)
    dic_resultados[consulta] = lista_doc
    #print(lista_resultados)

arquivo_resultados.close()

medida_f = 0
r_precisao = []
tabela_precisoes = pd.DataFrame(0.0, index=range(1,101) ,columns=["precisao@5","precisao@10"])
media_precisao = 0
media_media_precisao = 0
dcg = [0]*10
media_dcg = [0]*10
rr = 0
media_rr = 0

onze_recall_total = [0]*11
onze_recall_consulta = [0]*11
for chave,valor in  dic_resultados.items():
    media_precisao = 0

    dic_consulta = dic_esperados[chave]
    num_recuperados = 0.0
    num_recuperados_relevantes = 0.0
    num_relevantes = len(dic_consulta)

    for doc in valor:
        num_recuperados += 1      
        if doc in dic_consulta.keys(): num_recuperados_relevantes += 1
        precisao = 100*(num_recuperados_relevantes/num_recuperados)
        recall = math.floor(100*(num_recuperados_relevantes/num_relevantes))  / 10
        recall = int(recall)
        onze_recall_consulta[recall] = max(onze_recall_consulta[recall],precisao)

        if num_recuperados == 5:
            chave = int(chave)
            tabela_precisoes.loc[chave]['precisao@5'] = precisao/100

        if num_recuperados == 10:
            chave = int(chave)
            tabela_precisoes.loc[chave]['precisao@10'] = precisao/100
        
        if num_recuperados == num_relevantes:
            r_precisao.append(num_recuperados_relevantes/num_relevantes)

        if num_recuperados <= num_relevantes:
            media_precisao += (num_recuperados_relevantes/num_recuperados)/num_relevantes

        if num_recuperados_relevantes == 1:
            rr = 1/num_recuperados

        if int(num_recuperados) <= 10:
            if int(num_recuperados) == 1: 
                dcg[int(num_recuperados)-1] = (2**num_recuperados_relevantes - 1)/(math.log(1+num_recuperados))
                continue
            dcg[int(num_recuperados-1)] = dcg[int(num_recuperados-2)] + (2**num_recuperados_relevantes - 1)/(math.log(1+num_recuperados))
    
    media_media_precisao += media_precisao/100
    media_rr += rr/100
    for i in range(len(dcg)):
        media_dcg[i] += dcg[i]/100
    

    for i in range(len(onze_recall_total)):
        onze_recall_total[i] = max(onze_recall_consulta[i],onze_recall_total[i])

maior_ate_p = 0
lista_x = []
for i in range(len(onze_recall_total)):
    onze_recall_total[i] = int( max(onze_recall_total[i:]) )
    lista_x.append(10*i)
    
print(onze_recall_total)
print(lista_x)

#tabela_precisoes.to_csv("../AVALIA/" + config[3], sep=';', encoding='utf-8')

tabela_map_mrr = pd.DataFrame(data=[[media_media_precisao,media_rr]], index=["valores"] ,columns=["map","mrr"])
 
#tabela_map_mrr.to_csv("../AVALIA/" + config[5], sep=';', encoding='utf-8')

#plt.plot( lista_x, onze_recall_total, color='blue', linestyle='solid', linewidth = 3, marker='o', markerfacecolor='black', markersize=6)
  

#plt.ylim(0,100)
#plt.xlim(0,100)
  

#plt.xlabel('recall')

#plt.ylabel('precisão')
  
#plt.title('gráfico 11 pontos precisão recall')

#plt.savefig("../AVALIA/" + config[2])


#plt.hist(r_precisao)

#plt.savefig("../AVALIA/" + config[4])


plt.plot( [1,2,3,4,5,6,7,8,9,10], media_dcg, color='purple', linestyle='solid', linewidth = 3, marker='o', markerfacecolor='black', markersize=6)
  

plt.ylim(0,1)
plt.xlim(1,10)
  

plt.xlabel('ranking n')

plt.ylabel('dcg')
  
plt.title('gráfico media dcg')

plt.savefig("../AVALIA/" + config[6])
