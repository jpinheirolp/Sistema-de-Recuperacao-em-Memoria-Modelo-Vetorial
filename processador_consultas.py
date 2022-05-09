from bs4 import BeautifulSoup
from unidecode import unidecode

arquivo_config = open('PC.CFG', 'r')
config = []

for linha in arquivo_config:
    linha = linha.split("=")[1]
    linha = linha.replace("<","")
    linha = linha.replace(">","")
    linha = linha.replace("\n","")
    config.append(linha)

arquivo_config.close()

print(config)

arquivo_leitura = open('CysticFibrosis2-20220501/data/' + config[0],'r')

conteudo_leitura = arquivo_leitura.read()
soup = BeautifulSoup(conteudo_leitura,'xml')
numeros_consultas = soup.find_all('QueryNumber')
textos_consultas = soup.find_all('QueryText')
documentos_consultas = soup.find_all('Records')

arquivo_escrita1 = open(config[1], 'w')

texto_arquivo = ["QueryNumber;QueryText\n"]

for i in range(len(numeros_consultas)):
    
    numero_linha = numeros_consultas[i].get_text()
    texto_linha = textos_consultas[i].get_text()
    texto_linha = texto_linha.replace(";" , "")
    texto_linha = texto_linha.replace("\n" , "")
    texto_linha = unidecode(texto_linha)
    texto_linha = texto_linha.upper()
    

    texto_arquivo.append(numero_linha + ";" + texto_linha + "\n")

arquivo_escrita1.writelines(texto_arquivo)
arquivo_escrita1.close()

arquivo_escrita2 = open(config[2], 'w')

texto_arquivo = ["QueryNumber;DocNumber;DocVotes\n"]

for i in range(len(numeros_consultas)):
    
    numero_linha = numeros_consultas[i].get_text()
    documento_linha = documentos_consultas[i]
    votos_documento = documento_linha.find_all('Item')
    for voto in votos_documento:
        numero_documento = voto.get_text()
        valor_voto = voto["score"]
        numero_votos = len(valor_voto) - valor_voto.count("0")
        
        texto_arquivo.append(numero_linha + ";" + numero_documento + ";" + str(numero_votos) + "\n")

arquivo_escrita2.writelines(texto_arquivo)
arquivo_escrita2.close()
