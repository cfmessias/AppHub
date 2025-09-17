# -*- coding: utf-8 -*-
import os, sys, contextlib, runpy
import streamlit as st
import base64, requests, importlib
import pandas as pd

# ---------- Config ----------
st.set_page_config(page_title="Hub de Apps", page_icon="🧭", layout="wide", initial_sidebar_state="collapsed")

# ---------- CSS (sem sidebar + largura total) ----------
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"],
[data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] { display:none!important; width:0!important; }
section.main{ margin-left:0!important; }
.main .block-container{ max-width:100%!important; width:100%!important; padding:1rem; }
.subtitle{ color:#6b7280; font-size:0.95rem; margin-top:-.4rem; }
.back-wrap{ position:sticky; top:.5rem; z-index:100; }
</style>
""", unsafe_allow_html=True)

ROOT = os.path.dirname(os.path.abspath(__file__))

# ---------- Helpers ----------
import sys, os

def use_local_packages(app_dir: str, names=("services","views","utils","cinema","music","podcasts")):
    """Faz com que imports como 'from services...' e 'from views...' usem a pasta da app atual."""
    # 1) limpa do cache quaisquer módulos homónimos já carregados (de outras apps)
    for n in names:
        for k in [k for k in list(sys.modules.keys()) if k == n or k.startswith(n + ".")]:
            sys.modules.pop(k, None)
    # 2) prioriza diretórios da app: <app_dir>/<name>… e por fim a raiz da app
    order = [os.path.join(app_dir, n) for n in names if os.path.isdir(os.path.join(app_dir, n))]
    order.append(app_dir)
    for p in reversed(order):
        if p in sys.path: sys.path.remove(p)
    sys.path[:0] = order

def go(view: str | None):
    qp = st.query_params
    if view: qp["view"] = view
    else: qp.pop("view", None)

@contextlib.contextmanager
def pushd(new_dir: str):
    old = os.getcwd()
    try:
        os.chdir(new_dir); yield
    finally:
        os.chdir(old)

@contextlib.contextmanager
def mount_app(app_dir: str):
    """
    Isola a app:
      - purga módulos homónimos (views/services/utils/…)
      - coloca <app_dir> e subpastas relevantes no topo do sys.path (por esta ordem)
      - entra no CWD da app (ficheiros relativos)
    """
    old_path = list(sys.path)
    top_pkgs = ("views","services","utils","providers","components","models",
                "cinema","music","radio","podcasts","tv","video","data")

    # purga de cache
    for pkg in top_pkgs:
        for k in [k for k in list(sys.modules.keys()) if k == pkg or k.startswith(pkg + ".")]:
            sys.modules.pop(k, None)

    # priorizar paths da app
    expose = []
    for pkg in top_pkgs:
        p = os.path.join(app_dir, pkg)
        if os.path.isdir(p): expose.append(p)
    expose.append(app_dir)

    for p in reversed(expose):
        if p in sys.path: sys.path.remove(p)
    sys.path[:0] = expose

    try:
        with pushd(app_dir):
            yield
    finally:
        sys.path = old_path

def run_file(app_dir: str, filename: str):
    """Executa um ficheiro como __main__ e RESTAURA set_page_config no fim."""
    
    path = os.path.join(app_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    orig_set_page_config = getattr(st, "set_page_config", None)
    try:
        # impedir set_page_config duplicado DENTRO da app filha
        st.set_page_config = lambda *a, **k: None
        runpy.run_path(path, run_name="__main__")
    finally:
        # 🔧 ponto crucial: repor a função original para o Hub
        if orig_set_page_config is not None:
            st.set_page_config = orig_set_page_config


# (opcional) shim p/ Demografia se o CSV vier com labels alternativos
@contextlib.contextmanager
def patch_demografia_columns():
    
    _orig = pd.read_csv
    def _shim(*a, **k):
        df = _orig(*a, **k)
        ren = {}
        if "Regiao" not in df.columns:
            for c in ("Região","Region","REGIAO","regiao","Região "):
                if c in df.columns: ren[c] = "Regiao"; break
        if "Subregiao" not in df.columns:
            for c in ("Subregião","Subregion","SUBREGIAO","subregiao"):
                if c in df.columns: ren[c] = "Subregiao"; break
        if "Pais" not in df.columns:
            for c in ("País","Country","Country or area","PAIS","pais"):
                if c in df.columns: ren[c] = "Pais"; break
        return df.rename(columns=ren) if ren else df
    pd.read_csv = _shim
    try: yield
    finally: pd.read_csv = _orig

# ---------- Router ----------
qp = st.query_params
view = qp.get("view", None)

# capta callbacks OAuth (ex.: Spotify) e envia para a vista correta
if ("code" in qp or "state" in qp) and view != "multimedia4all":
    qp["view"] = "multimedia4all"
    st.rerun()

if view is None:
    # Hub
    st.title("📦 Hub de Aplicações")
    st.caption("Uma app Streamlit a agregar 4 projetos.")

    c1, c2, c3, c4 = st.columns(4, gap="large")
    with c1:
        st.markdown("### 🌦️ Meteo")
        st.markdown('<div class="subtitle">Previsões, histórico, sismicidade e cenários.</div>', unsafe_allow_html=True)
        if st.button("Abrir Meteo", type="primary", use_container_width=True): go("meteo")
    with c2:
        st.markdown("### 🌍 Demografia")
        st.markdown('<div class="subtitle">Indicadores e hierarquias demográficas.</div>', unsafe_allow_html=True)
        if st.button("Abrir Demografia", type="primary", use_container_width=True): go("demografia")
    with c3:
        st.markdown("### 🎵📽️ multimedia4all")
        st.markdown('<div class="subtitle">Música, cinema, rádio, podcasts, playlists.</div>', unsafe_allow_html=True)
        if st.button("Abrir multimedia4all", type="primary", use_container_width=True): go("multimedia4all")
    with c4:
        st.markdown("### 🧩 Passatempos")
        st.markdown('<div class="subtitle">Cruzadas, sinónimos, lógica, e mais.</div>', unsafe_allow_html=True)
        if st.button("Abrir Passatempos", type="primary", use_container_width=True): go("passatempos")

    st.divider()
    st.markdown("💡 Navega só com estes botões; não existe sidebar.")

else:
    # Páginas internas
    st.markdown('<div class="back-wrap">', unsafe_allow_html=True)
    if st.button("← Voltar ao Hub"): go(None)
    st.markdown('</div>', unsafe_allow_html=True)

    try:
        if view == "meteo":
            app_dir = os.path.join(ROOT, "Meteo")
            with mount_app(app_dir):
                st.title("🌦️ Meteo")
                run_file(app_dir, "app.py")

        elif view == "demografia":
            app_dir = os.path.join(ROOT, "Demografia")
            USE_DEMOG_SHIM = False  # põe True se o CSV vier com 'Região/Region' etc.
            ctx = (mount_app(app_dir), patch_demografia_columns()) if USE_DEMOG_SHIM else (mount_app(app_dir),)
            with contextlib.ExitStack() as stack:
                for cm in ctx: stack.enter_context(cm)
                st.title("🌍 Demografia")
                run_file(app_dir, "app.py")

        elif view == "multimedia4all":
            app_dir = os.path.join(ROOT, "multimedia4all")

            # 1) priorizar pacotes desta app (sem purgas globais)
            with pushd(app_dir):
                for p in [os.path.join(app_dir, s) for s in ("services","views") if os.path.isdir(os.path.join(app_dir, s))] + [app_dir]:
                    if p in sys.path: sys.path.remove(p)
                    sys.path.insert(0, p)

                st.title("🎵📽️ multimedia4all")

                # 2) colocar credenciais no ambiente (lidas do topo OU da secção [multimedia4all])
                sec  = dict(st.secrets.get("multimedia4all", {}))
                cid  = sec.get("SPOTIFY_CLIENT_ID")     or st.secrets.get("SPOTIFY_CLIENT_ID", "")
                csec = sec.get("SPOTIFY_CLIENT_SECRET") or st.secrets.get("SPOTIFY_CLIENT_SECRET", "")
                red  = sec.get("SPOTIFY_REDIRECT_URI")  or st.secrets.get("SPOTIFY_REDIRECT_URI", "")
                if cid:  os.environ["SPOTIPY_CLIENT_ID"]     = os.environ["SPOTIFY_CLIENT_ID"]     = str(cid)
                if csec: os.environ["SPOTIPY_CLIENT_SECRET"] = os.environ["SPOTIFY_CLIENT_SECRET"] = str(csec)
                if red:  os.environ["SPOTIPY_REDIRECT_URI"]  = os.environ["SPOTIFY_REDIRECT_URI"]  = str(red)

                # 3) reimportar SÓ o módulo de lookup e injetar token client-credentials (para Podcasts)
                try:
                    import importlib, base64, requests
                    sys.modules.pop("services.music.spotify.lookup", None)  # limpa só este
                    lookup = importlib.import_module("services.music.spotify.lookup")

                    token = ""
                    if cid and csec:
                        auth = base64.b64encode(f"{cid}:{csec}".encode()).decode()
                        r = requests.post(
                            "https://accounts.spotify.com/api/token",
                            headers={"Authorization": f"Basic {auth}"},
                            data={"grant_type": "client_credentials"},
                            timeout=10,
                        )
                        if r.ok:
                            token = (r.json() or {}).get("access_token", "") or ""

                    if token:
                        # faz com que get_spotify_token_cached() devolva SEMPRE um token válido
                        lookup.get_spotify_token_cached = (lambda _tok=token: _tok)
                except Exception:
                    pass  # se falhar, a app continua; só não “salvamos” os podcasts

                # 4) correr a app normalmente (Music/search volta a usar o teu OAuth de utilizador)
                run_file(app_dir, "app.py")



        elif view == "passatempos":
            app_dir = os.path.join(ROOT, "PassaTempos")
            with mount_app(app_dir):
                st.title("🧩 Passatempos")
                for fname in ("passatempos.py","WOW3.py","cruzadas2.py","sinonimos.py","sinonimos2.py","x_wing_solver.py","app.py"):
                    try:
                        run_file(app_dir, fname); break
                    except FileNotFoundError:
                        continue
        else:
            st.warning("Página desconhecida. A voltar ao hub…"); go(None)

    except Exception as e:
        st.error(f"❌ Erro ao montar a página '{view}': {e}")
        st.exception(e)
