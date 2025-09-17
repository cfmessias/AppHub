import streamlit as st
import requests

def obter_sinonimos(palavra):
    url = "https://api.datamuse.com/words"
    params = {
        "rel_syn": palavra,
        "max": 10
    }
    resposta = requests.get(url, params=params)

    if resposta.status_code == 200:
        dados = resposta.json()
        return [item["word"] for item in dados]
    else:
        st.error(f"Erro ao aceder à API: {resposta.status_code}")
        return []

# Interface Streamlit
st.title("Descobre Sinónimos")
st.write("Insere uma palavra para obter possíveis sinónimos (via Datamuse API).")

palavra = st.text_input("Palavra:", "")

if st.button("Procurar Sinónimos"):
    if palavra.strip() != "":
        sinonimos = obter_sinonimos(palavra.strip())
        if sinonimos:
            st.success(f"Sinónimos de '{palavra}':")
            st.write(", ".join(sinonimos))
        else:
            st.warning("Nenhum sinónimo encontrado.")
    else:
        st.warning("Por favor, insere uma palavra válida.")
