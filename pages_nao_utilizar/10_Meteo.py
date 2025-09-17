# -*- coding: utf-8 -*-
import os, sys, importlib
import streamlit as st

# evitar múltiplos set_page_config vindos da app importada
st.set_page_config = lambda *a, **k: None

# esconder sidebar nesta página também
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"] { display: none !important; }
.main .block-container { padding-top: 1rem; padding-left: 1rem; padding-right: 1rem; }
</style>
""", unsafe_allow_html=True)

ROOT = os.path.dirname(os.path.dirname(__file__))
METEO_DIR = os.path.join(ROOT, "Meteo")
if ROOT not in sys.path: sys.path.insert(0, ROOT)
if METEO_DIR not in sys.path: sys.path.insert(0, METEO_DIR)

st.title("🌦️ Meteo")

def _mount_and_run(module_path: str, fn_candidates=("run", "main", "app", "render", "start")):
    mod = importlib.import_module(module_path)
    for fn in fn_candidates:
        if hasattr(mod, fn) and callable(getattr(mod, fn)):
            return getattr(mod, fn)()
    return None

try:
    _mount_and_run("Meteo.app")
except Exception as e:
    st.error(f"❌ Erro ao montar Meteo.app: {e}")
    st.exception(e)
