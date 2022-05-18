from bs4 import BeautifulSoup
from unidecode import unidecode
import re
from porter_stemmer import PorterStemmer

ps = PorterStemmer()

print("abandon",ps.stem("abandon", 0,len("abandon")-1))

arquivo_config = open('GLI.CFG', 'r')
colecao_docs = []
arquivo_escrita = ""
flag_stemmer = False

for linha in arquivo_config:
    if not("=" in linha):
        if linha.replace("\n","").replace(" ","") == "STEMMER": 
            flag_stemmer = True
        continue
    nome_linha , conteudo_linha = linha.split("=")
    print(nome_linha,conteudo_linha)
    
    conteudo_linha = conteudo_linha
    conteudo_linha = conteudo_linha.replace("<","")
    conteudo_linha = conteudo_linha.replace(">","")
    conteudo_linha = conteudo_linha.replace("\n","")

    if nome_linha != "LEIA": 
        arquivo_escrita = conteudo_linha
        nome_arquivo, tipo_arquivo = arquivo_escrita.split(".")
        nome_arquivo += "-STEMMER" if flag_stemmer else "-NOSTEMMER"
        arquivo_escrita = nome_arquivo + "." + tipo_arquivo
        break

    colecao_docs.append(conteudo_linha)


arquivo_config.close()

print(colecao_docs, arquivo_escrita)

colecao_palavras = {}

for doc in colecao_docs:
    arquivo_leitura = open('../CysticFibrosis2-20220501/data/' + doc,'r')

    conteudo_leitura = arquivo_leitura.read()
    soup = BeautifulSoup(conteudo_leitura,'xml')
    textos_consultas = soup.find_all('RECORD')
    for i in range(len(textos_consultas)):
        numero_texto = textos_consultas[i].find("RECORDNUM").get_text()
        numero_texto = int(numero_texto)
        conteudo_texto = textos_consultas[i].find("ABSTRACT")
        if not(conteudo_texto):
            conteudo_texto = textos_consultas[i].find("EXTRACT")
            if not(conteudo_texto): continue
        conteudo_texto = conteudo_texto.get_text()
        #conteudo_texto = conteudo_texto.replace("\n","")
        
        palavras_texto = re.sub("[^a-zA-Z]+", " ", conteudo_texto)
        palavras_texto = re.split("['-();:,.!? \n]", palavras_texto)

        #palavras_texto = conteudo_texto.split(" ")
        for palavra in palavras_texto:
            palavra = ps.stem(palavra, 0,len(palavra)-1) if flag_stemmer else palavra
            palavra = unidecode(palavra.upper())

            if palavra in colecao_palavras.keys():
                colecao_palavras[palavra].append(numero_texto)
                continue
            colecao_palavras[palavra] = [numero_texto]
    arquivo_leitura.close()

#print(colecao_palavras)

arquivo_escrita = open("../RESULT/" + arquivo_escrita, 'w')
texto_arquivo = []

for chave,valor in colecao_palavras.items():
    texto_arquivo.append(chave + ";" + str(valor) + "\n")

arquivo_escrita.writelines(texto_arquivo)
arquivo_escrita.close()