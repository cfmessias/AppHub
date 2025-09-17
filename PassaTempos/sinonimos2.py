import streamlit as st
import requests
from bs4 import BeautifulSoup

# Datamuse
def obter_sinonimos_datamuse(palavra, numero_letras=None):
    url = "https://api.datamuse.com/words"
    params = {"rel_syn": palavra, "max": 100}
    try:
        resposta = requests.get(url, params=params)
        if resposta.status_code == 200:
            dados = resposta.json()
            sinonimos = [item["word"] for item in dados]
            if numero_letras:
                sinonimos = [s for s in sinonimos if len(s) == numero_letras]
            return sinonimos
    except:
        pass
    return []

# Dicio.com.br (scraping)
def obter_sinonimos_dicio(palavra, numero_letras=None):
    try:
        url = f"https://www.dicio.com.br/{palavra.lower()}/"
        resposta = requests.get(url)
        if resposta.status_code != 200:
            return []
        soup = BeautifulSoup(resposta.text, "html.parser")
        bloco = soup.find("p", class_="adicional sinonimos")
        if not bloco:
            return []
        texto = bloco.get_text(strip=True)
        partes = texto.split(":")
        if len(partes) < 2:
            return []
        lista_sinonimos = [s.strip() for s in partes[1].split(",")]
        if numero_letras:
            lista_sinonimos = [s for s in lista_sinonimos if len(s) == numero_letras]
        return lista_sinonimos
    except:
        return []

# Interface
st.title("🔠 Ajuda para Palavras Cruzadas")
palavra = st.text_input("Palavra de referência:")
num_letras = st.number_input("Número de letras (opcional):", min_value=1, max_value=30, step=1, format="%d", value=None)

if st.button("🔍 Procurar sinónimos"):
    if palavra.strip():
        st.info("A procurar sinónimos em várias fontes...")
        resultados = set()

        resultados.update(obter_sinonimos_datamuse(palavra.strip(), numero_letras=num_letras))
        if len(resultados) < 5:
            resultados.update(obter_sinonimos_dicio(palavra.strip(), numero_letras=num_letras))

        if resultados:
            st.success("Sinónimos encontrados:")
            st.write(", ".join(sorted(resultados)))
        else:
            st.warning("Nenhum sinónimo encontrado.")
    else:
        st.warning("Por favor, insere uma palavra válida.")
