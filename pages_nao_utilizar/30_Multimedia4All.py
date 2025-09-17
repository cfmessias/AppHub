# -*- coding: utf-8 -*-
import os, sys, importlib
import streamlit as st
st.set_page_config = lambda *a, **k: None

st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="collapsedControl"] { display: none !important; }
.main .block-container { padding-top: 1rem; padding-left: 1rem; padding-right: 1rem; }
</style>
""", unsafe_allow_html=True)

ROOT = os.path.dirname(os.path.dirname(__file__))
MM_DIR = os.path.join(ROOT, "multimedia4all")
if ROOT not in sys.path: sys.path.insert(0, ROOT)
if MM_DIR not in sys.path: sys.path.insert(0, MM_DIR)

st.title("🎵📽️ multimedia4all")

def _mount_and_run(module_path: str, fn_candidates=("run", "main", "app", "render", "start")):
    mod = importlib.import_module(module_path)
    for fn in fn_candidates:
        if hasattr(mod, fn) and callable(getattr(mod, fn)):
            return getattr(mod, fn)()
    return None

try:
    _mount_and_run("multimedia4all.app")
except Exception as e:
    st.error(f"❌ Erro ao montar multimedia4all.app: {e}")
    st.exception(e)
