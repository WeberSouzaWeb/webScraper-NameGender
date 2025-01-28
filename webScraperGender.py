# Web Scraper

# Imports
import os
import re
import csv
import pickle
import requests
from bs4 import BeautifulSoup


# Variável com o endereço da página
# Inicie o servidor web com o comando: python -m http.server
PAGE = "http://localhost:8000/index.html"


# Função para extrair os dados
def extrai_dados(cb):

    # Extraindo o nome 
    str_name = cb.find('span', class_='name').text

    # Extraindo o genero da pessoa e converte para char
    str_gender = cb.find('span', class_='gender').text
    gender = str(str_gender)

    # Se o genero  não for M ou F, geramos mensagem de erro
    assert gender == "M" or "F" , f"Esperando que o genero seja binario e não {gender}"

    # Extraindo a quantidade de generos do nome
    str_count = cb.find('span', class_='count').text

    # Removemos as vírgulas
    count = int(str_count.replace(',', ''))

    # Se a quantidade não for maior que zero, geramos mensagem de erro
    assert count > 0, f"Esperando que a quantidade seja positivo e não  {count}"

    # Extraindo a probabilidade
    probability = float(cb.find('span', class_='probability').text)

    # Se a probabilidade não for maior que zero, geramos mensagem de erro
    assert probability > 0, f"Expecting probabilidade to be positive"

    # Geramos um dicinário para cada linha extraída
    linha = dict(name=str_name, gender=gender, count=count, probability=probability)
    return linha


def processa_blocos(soup):

    # Extraindo informações de repetidas divisões (tag div)
    gender_blocks = soup.find_all('div', class_='entry_block')
    if not gender_blocks:
            print("Nenhum bloco de carros encontrado na página.")
            return
    # Lista vazia para receber as linhas
    linhas = []

    # Loop pelos blocos de dados de gender
    for gen in gender_blocks:
        linha = extrai_dados(gen)
        linhas.append(linha)

    print(f"\nTemos {len(linhas)} linhas de dados retornadas do scraping da página!")

    # Imprime a primeira e a última linha
    print("\nPrimeira linha copiada:")
    print(linhas[0])

    print("\nÚltima linha copiada:")
    print(linhas[-1])
    print("\n")

    # Grava o resultado em csv
    with open("dados_copiados_v1.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames = linha.keys())
        writer.writeheader()
        writer.writerows(linhas)


# Execução principal do programa
if __name__ == "__main__":

    # Arquivo para guardar os dados copiados em cache
    filename = 'dados_copiados_v1.pickle'
    
    result = None
    # Se o arquivo já existir, carregamos o arquivo
    if os.path.exists(filename):
        try:
            with open(filename, 'rb') as f:
                print(f"\nCarregando o cache a partir do arquivo {filename}")
                result = pickle.load(f)
        except (pickle.UnpicklingError, EOFError) as e:
            print(f"\nErro ao carregar o cache: {e}")
            result = None
    else:
        result = None
 

 # Se não, copiamos da página web
    if result is None:
        try:
            print(f"\nCopiando dados da página {PAGE}.")
            result = requests.get(PAGE, timeout=10) 
            result.raise_for_status()  # Raise HTTPError for erro responses
            with open(filename, 'wb') as f:
                print(f"\nGravando o cache em {filename}")
                pickle.dump(result, f)
        except requests.exceptions.RequestException as e:
            print(f"\nErro ao acessar a página: {e}")
            result = None  

    # Se o status for diferente de 200, geramos mensagem de erro
    assert result.status_code == 200, f"Obteve status {result.status_code} verifique sua conexão!"
    if result:
        # Verifica se o conteúdo não está vazio
        texto_web = result.text.strip()
        if not texto_web:
            raise ValueError("O texto da página está vazio!")

        # Faz o parser do texto da página
        soup = BeautifulSoup(texto_web, 'lxml')  # Use 'lxml' for better parsing
    else:
        raise RuntimeError("Nenhum resultado disponível para parsing!")

    # Processa os dados de carros
    processa_blocos(soup)