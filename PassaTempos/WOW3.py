import streamlit as st
import itertools
import requests
from functools import lru_cache

st.markdown("<h4 style='margin-bottom: 0.5em;'>🧩 Gerador de Palavras Válidas com Letras Repetidas (PT)</h4>", unsafe_allow_html=True)
@lru_cache(maxsize=2048)
def validar_datamuse(palavra):
    """Valida palavra usando Datamuse API."""
    url = "https://api.datamuse.com/words"
    params = {"sp": palavra, "max": 1}
    try:
        resposta = requests.get(url, params=params, timeout=3)
        if resposta.status_code == 200:
            resultados = resposta.json()
            return any(item["word"].lower() == palavra.lower() for item in resultados)
    except Exception:
        pass
    return False

@lru_cache(maxsize=2048)
def validar_priberam(palavra):
    """Valida palavra usando Priberam (dicionário de português) via scraping."""
    url = f"https://dicionario.priberam.org/{palavra}"
    try:
        resposta = requests.get(url, timeout=3)
        # Palavra válida se existe a secção de aceitação do Priberam
        return "não foi encontrada" not in resposta.text.lower()
    except Exception:
        pass
    return False

@lru_cache(maxsize=2048)
def validar_wiktionary(palavra):
    """Valida palavra usando Wiktionary API."""
    url = f"https://pt.wiktionary.org/w/api.php"
    params = {
        "action": "query",
        "titles": palavra,
        "format": "json"
    }
    try:
        resposta = requests.get(url, params=params, timeout=3)
        data = resposta.json()
        pages = data.get("query", {}).get("pages", {})
        return not "-1" in pages
    except Exception:
        pass
    return False

def validar_palavra(pt):
    """Valida uma palavra em todas as fontes."""
    return (
        validar_datamuse(pt) or
        validar_priberam(pt) or
        validar_wiktionary(pt)
    )

def palavra_respeita_molde(palavra, molde):
    """Verifica se a palavra cumpre o molde (letras nas posições corretas)"""
    return all(m == "_" or m.lower() == p.lower() for m, p in zip(molde, palavra))

def gerar_palavras_validas(letras, tamanho, molde=None):
    """Gera permutações, filtra por molde e por palavras reais"""
    letras = letras.lower()
    todas = set(''.join(p) for p in itertools.permutations(letras, tamanho))
    
    # Filtra por molde se fornecido
    if molde:
        molde = molde.lower()
        todas = [p for p in todas if palavra_respeita_molde(p, molde)]

    # Valida palavras
    palavras_validas = [p for p in todas if validar_palavra(p)]
    return palavras_validas, todas

# Interface Streamlit
st.title("🧩 Gerador de Palavras Válidas com Letras Repetidas (PT)")

st.markdown("""
Insere letras (pode incluir acentos e repetir letras).  
Exemplo: `rarroc`, `ação`, `amora`
""")

letras_input = st.text_input("Letras:", value="rarroc")

if letras_input:
    tamanho = st.number_input(
        "Tamanho da palavra:", min_value=1, max_value=len(letras_input), step=1
    )
    molde = st.text_input(
        "Molde da palavra (usa '_' para desconhecidos):", value="_"*tamanho
    )

    if len(molde) != tamanho:
        st.warning("O molde deve ter o mesmo número de letras indicado no tamanho.")
    elif st.button("🔍 Gerar Palavras"):
        st.info("A procurar palavras válidas em múltiplos dicionários...")
        resultado, todas = gerar_palavras_validas(letras_input, tamanho, molde)
        
        if resultado:
            st.success(f"Encontradas {len(resultado)} palavra(s) reconhecidas:")
            st.markdown(", ".join(sorted(resultado)))
        else:
            st.warning("Nenhuma palavra reconhecida nos dicionários. Eis as possíveis combinações:")
            st.markdown(", ".join(sorted(todas)))
            st.info("Talvez alguma combinação seja válida mas não está listada nos dicionários online.")