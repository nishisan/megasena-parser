#!/usr/bin/env python
# coding: utf-8

# # Importador de Resultados da Megasena
# 
# Para fins educativos, eu criei um pequeno notebook que importa os dados dos jogos da megasena a partir do site da caixa (https://loterias.caixa.gov.br/Paginas/Download-Resultados.aspx).<br>
# Não preciso dizer que o código é apresentado como é sem nenhuma garantia ou reponsabilidade de uso do mesmo.
# 

# In[1]:


import pandas as pd
import urllib.request
import ssl
import json
import itertools
import numpy as np
from bs4 import BeautifulSoup
# import threading
from threading import Thread
from threading import current_thread


# A Função abaixo serve para remover os espaços e quebras de linhas das celulas do BeautifulSoup.
# Com certeza deve haver um jeito mais elegante de fazer

# In[2]:


#
# Remove espaços e quebras de linha da celular do BeautifulSoup
#
def stripText(a):
    if a:
        return ''.join(a.text.split())


# In[3]:


#
# Faz a requisição HTTP para o site da caixa
# 
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode    = ssl.CERT_NONE
#
# URL Abaixo é a que rendeiza a tabela apresentada no link: https://loterias.caixa.gov.br/Paginas/Download-Resultados.aspx
#
url = 'https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados?modalidade=Mega-Sena'
req = urllib.request.Request(url=url)
f   = urllib.request.urlopen(req,context=ctx)
js  = f.read().decode('utf-8')
js  = json.loads(js)


# In[4]:


#
# Aqui a gente pega o HTML que veio no JSON da caixa e intepreta ele como HTML :)
#
soup = BeautifulSoup(js['html'])


# ### Sobre a estrutura de dados
# A estrutura de dados que é retornada pela tabela é um tanto quanto quanto confusa, com tabelas dentro de tabelas, então o código abaixo lida com essa complexidade para tentar extrair de forma simples as colunas que são renderizadas no browser.<br>
# No final desta célula , teremos uma variável 'head', com a lista dos campos e uma variável data, com as linhas e os valores dos campos.

# In[5]:


#
# Extrai os resultados da Megasena do Site da Caixa :)
#
table  = soup.find('table')
#
# head vai conter a lista de colunas com nomes :)
#
head   = table.find_all('thead',recursive=False)
head   = head[0].findChildren('tr',recursive=False)
head   = head[0].findChildren('th',recursive=False)
head   = list(map(stripText,head))
bodies = table.find_all('tbody',recursive=False)
#
# data, é uma lista de de listas com todas as colunas
#
data   = []
for body in bodies:
    a     = body.find('tr',recursive=False)
    cells = a.findChildren('td',recursive=False)
    row_data  = []
    for cell in cells:
        text = cell.text
        text = ''.join(text.split())
        row_data.append(text)
    data.append(row_data)
    


# ### Resultado
# Abaixo você pode ver a lista de resultados dos jogos imprimida na ordem, note que eu não fiz nenhum tratamento com relação ao tipo de dado, mas eu acho que serve como uma ponto de partida para seus estudos.
# Ah sim!, eu só imprimi as colunas dos resultados, mas poderia ser impresso tudo.

# In[6]:


#
# Imprimi todos os resultados por sorteio
#
countDict = {}
for result in data:

    numbers = result[2:8]

    for dezena in numbers:
        if not dezena in countDict:
            countDict[dezena]  = 1
        else:
            countDict[dezena] += 1
            
    
    #
    # Imprimi apenas os resultados dos jogos.
    #
    # print(result[0],result[2:8])
    #
    # Imprimi todos os dados da tabela
    #
    # print(result[0],result)

sortedDict = sorted(countDict.items(), key=lambda x:x[1],reverse=True)
for x in sortedDict:
    print('Number:[' + x[0] + '] Repeated: ['+str(x[1])+' Times]')
    


# In[7]:


#
# Agora vamos criar algumas combinações
#
duplas     = list(itertools.combinations(countDict.keys(), 2))
trinas     = list(itertools.combinations(countDict.keys(), 3))
quadruplas = list(itertools.combinations(countDict.keys(), 4))
quintuplas = list(itertools.combinations(countDict.keys(), 5))
sextuplas  = list(itertools.combinations(countDict.keys(), 6))

print(len(duplas))
print(len(trinas))
print(len(quadruplas))
print(len(quintuplas))
print(len(sextuplas))


# In[9]:


#
# Vamos testar por Ocorrencia qual grupo apresentou mais resultados
#
combinationCalc = {}
def addResult(m):
    combinationCalc = Merge(combinationCalc, m)

def checkMaches(combinations):
    m      = {}
    index  = 0
    print("%s - Starting Checking :%d Records " %(current_thread().name,len(combinations)))
    for d in combinations:
        index +=1
        if index % 10 == 0:
            perctDone = index / len(combinations)
            perctDone = perctDone * 100
            print("%s - Current:[%d]: %s de %d(%s) Found: [%d] Matches" % (current_thread().name,index,'Processed',len(combinations),format(perctDone, ".2f"),len(m)))
        for sorteio in data:         
            result = np.in1d(d, sorteio[2:8]).all()
            if (result):
                #
                # List is matched
                #
                # print('Matche:' + str(d))
                # print(sorteio[2:8],sorteio[0])
                if str(d) not in m:
                    m[str(d)] = 1
                else:
                    m[str(d)] += 1
    addResult(m)
    print("%s - Done Checking :%d Records " %(current_thread().name,len(combinations)))


# In[ ]:


#
# Vamos quebrar as combinações em chunks
#

workload = np.array_split(duplas, 8)
threads  = []
threadId = 0
for w in workload:
    threadId+=1
    t = Thread(target=checkMaches,args=(w,),name='Thread-'+str(threadId))
    threads.append(t)
    t.start()
    

for t in threads:
    t.join()

