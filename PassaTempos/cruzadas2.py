import streamlit as st
import requests

def obter_sinonimos(palavra, num_letras=None):
    url = "https://api.datamuse.com/words"
    params = {"rel_syn": palavra, "max": 50}
    resposta = requests.get(url, params=params)
    if resposta.status_code == 200:
        lista = [item["word"] for item in resposta.json()]
        if num_letras:
            lista = [w for w in lista if len(w) == num_letras]
        return lista
    return []

def obter_relacionadas(palavra, num_letras=None):
    url = "https://api.datamuse.com/words"
    params = {"ml": palavra, "max": 50}
    resposta = requests.get(url, params=params)
    if resposta.status_code == 200:
        lista = [item["word"] for item in resposta.json()]
        if num_letras:
            lista = [w for w in lista if len(w) == num_letras]
        return lista
    return []

def obter_definicoes(palavra):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{palavra}"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        try:
            dados = resposta.json()
            definicoes = []
            for sentido in dados[0]['meanings']:
                for definicao in sentido['definitions']:
                    definicoes.append(definicao['definition'])
            return definicoes[:3]
        except Exception:
            return []
    return []

# Interface do Streamlit
st.title("🔠 Ajuda para Palavras Cruzadas")
palavra = st.text_input("Insere uma palavra ou pista curta:")
num_letras = st.number_input("Número de letras esperado (opcional):", min_value=1, max_value=30, step=1, format="%d", value=None)

if palavra:
    st.markdown(f"### 🔍 Resultados para: `{palavra}`")
    
    definicoes = obter_definicoes(palavra)
    if definicoes:
        st.subheader("📘 Definições")
        for d in definicoes:
            st.markdown(f"- {d}")

    sinonimos = obter_sinonimos(palavra, num_letras)
    if sinonimos:
        st.subheader("🟢 Sinónimos")
        st.markdown(", ".join(sinonimos))

    relacionadas = obter_relacionadas(palavra, num_letras)
    if relacionadas:
        st.subheader("🔵 Palavras relacionadas")
        st.markdown(", ".join(relacionadas))

    if not (definicoes or sinonimos or relacionadas):
        st.warning("⚠️ Nenhuma informação encontrada.")
