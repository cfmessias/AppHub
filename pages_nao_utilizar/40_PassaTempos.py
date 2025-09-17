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
PT_DIR = os.path.join(ROOT, "PassaTempos")
if ROOT not in sys.path: sys.path.insert(0, ROOT)
if PT_DIR not in sys.path: sys.path.insert(0, PT_DIR)

st.title("🧩 Passatempos")

def _mount_and_run_by_best_guess():
    candidates = [
        "PassaTempos.passatempos",
        "PassaTempos.WOW3",
        "PassaTempos.cruzadas2",
        "PassaTempos.sinonimos",
        "PassaTempos.sinonimos2",
        "PassaTempos.x_wing_solver",
    ]
    fn_candidates = ("run", "main", "app", "render", "start")
    last_err = None
    for modpath in candidates:
        try:
            mod = importlib.import_module(modpath)
            for fn in fn_candidates:
                if hasattr(mod, fn) and callable(getattr(mod, fn)):
                    return getattr(mod, fn)()
            return
        except Exception as e:
            last_err = e
            continue
    if last_err:
        raise last_err

try:
    _mount_and_run_by_best_guess()
except Exception as e:
    st.error(f"❌ Erro ao montar Passatempos: {e}")
    st.exception(e)
