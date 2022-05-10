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

tabela_consultas = pd.read_csv(config[1], sep=';', encoding="utf_8")