import streamlit as st
import matplotlib.pyplot as plt
from dados import carregar_dados
from graficos import grafico_evolucao, grafico_mortalidade_stack
import matplotlib.patches as mpatches
import io

# Aplica o estilo CSS personalizado
css = """
<style>
    [data-testid="stSidebar"] {
        min-width: 100px;
        max-width: 120px;
        background: linear-gradient(to left , #eaeded ,#137ea8);
        padding: 0.5rem;
        border-right: 1px solid #dee2e6;
    }

    .sidebar-title-vertical {
        writing-mode: vertical-lr;
        text-orientation: upright;
        font-size: 16px;
        font-weight: bold;
        color: white;
        text-align: center;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.2;
    }

    .stSelectbox {
        display: none; /* Esconde temporariamente a selectbox */
    }

    .stApp {
        background: linear-gradient(to left , #eaeded , #eaeded);
    }
</style>

"""

# Carregar dados
(
    df_pop, df_dens, df_racio, df_cresc,
    df_idade_media, df_taxa_alteracao_natural,
    df_nascimentos, df_obitos,
    df_esperanca_vida, df_esperanca_vida_homens80, df_esperanca_vida_mulheres80,
    df_mortalidade_antes40, df_mortalidade_antes60, df_mortalidade_entre15e50,
    df_taxa_migracao_liquida, df_mortalidade_entre15e50Homens, df_mortalidade_entre15e50Mulheres
) = carregar_dados()

# Grupos de gráficos
grupos = {
    "População e Estrutura": [
        (df_pop, "População Total", "Milhares de Habitantes", "Populacao"),
        (df_dens, "Densidade Populacional", "Habitantes/km²", "Densidade"),
        (df_racio, "Rácio de Género", "Homens por Mulher", "RacioGenero"),
        (df_cresc, "Taxa de Crescimento Populacional", "%", "Crescimento")
    ],
    "Natalidade e Mortalidade": [
        (df_nascimentos, "Nascimentos", "Milhares", "Nascimentos"),
        (df_obitos, "Óbitos", "Milhares", "Obitos"),
        (df_taxa_alteracao_natural, "Alteração Natural", "Milhares", "TaxaAlteracaoNatural"),
        (df_esperanca_vida, "Esperança de Vida", "Anos", "EsperancaVida")
    ],
    "Mortalidade Específica": [
        (df_mortalidade_antes40, "Mortalidade antes dos 40", "Óbitos/1.000 nascimentos", "MortalidadeAntes40"),
        (df_mortalidade_antes60, "Mortalidade antes dos 60", "Óbitos/1.000 nascimentos", "MortalidadeAntes60"),
        (df_mortalidade_entre15e50Homens, "Mortalidade 15–50 (Homens)", "Óbitos/1.000 vivos aos 15", "MortalidadeEntre15e50Homens"),
        (df_mortalidade_entre15e50Mulheres, "Mortalidade 15–50 (Mulheres)", "Óbitos/1.000 vivas aos 15", "MortalidadeEntre15e50Mulheres")
    ],
    "Indicadores Adicionais": [
        (df_idade_media, "Idade Média", "Anos", "IdadeMedia"),
        (df_taxa_migracao_liquida, "Migração Líquida", "Milhares", "TaxaMigracaoLiquida"),
        (df_esperanca_vida_homens80, "Esperança Vida aos 80 (Homens)", "Anos", "EsperancaVidaHomens80"),
        (df_esperanca_vida_mulheres80, "Esperança Vida aos 80 (Mulheres)", "Anos", "EsperancaVidaMulheres80")
    ]
}

# Interface
st.set_page_config(page_title="Indicadores Demográficos", layout="wide")
st.sidebar.markdown("""
<div class="sidebar-title-vertical">📊 INDICADORES DEMOGRÁFICOS</div>
""", unsafe_allow_html=True)

st.markdown(css, unsafe_allow_html=True)

# Criar tabs para os grupos principais
tab_grupos = st.tabs(["📊População e Estrutura", "📈Natalidade e Mortalidade", "📜Mortalidade Específica", "🔬Indicadores Adicionais"])

for tab, grupo_nome in zip(tab_grupos, grupos.keys()):
    with tab:
        # Criar legenda compacta
        fig_legend = plt.figure(figsize=(6, 0.4), dpi=300)
        ax_legend = fig_legend.add_axes([0, 0, 1, 1])
        ax_legend.axis('off')

        patches = [
            mpatches.Patch(color='orange', label='América'),
            mpatches.Patch(color='red', label='Europa'),
            mpatches.Patch(color='purple', label='Oceania'),
            mpatches.Patch(color='blue', label='África'),
            mpatches.Patch(color='green', label='Ásia')
        ]

        ax_legend.legend(
            handles=patches,
            loc='center',
            ncol=5,
            frameon=False,
            fontsize='xx-small',
            columnspacing=0.5,
            handlelength=1.0,
            handletextpad=0.4,
            borderpad=0.0
        )

        buf = io.BytesIO()
        fig_legend.savefig(buf, format="png", bbox_inches="tight", transparent=True, pad_inches=0)
        buf.seek(0)
        st.image(buf)

        # Gráficos do grupo
        subtab1, subtab2 = st.tabs(["Gráficos 1 e 2", "Gráficos 3 e 4"])

        with subtab1:
            fig, axs = plt.subplots(1, 2, figsize=(9.6, 3))
            for i in range(0, 2):
                df, titulo, ylabel, dado = grupos[grupo_nome][i]
                grafico_evolucao(df, titulo, ylabel, dado, 'linha', axs[i])
            fig.patch.set_alpha(0.0)
            st.pyplot(fig, transparent=True)

        with subtab2:
            fig, axs = plt.subplots(1, 2, figsize=(9.6, 3))
            for i in range(2, 4):
                df, titulo, ylabel, dado = grupos[grupo_nome][i]
                grafico_evolucao(df, titulo, ylabel, dado, 'linha', axs[i - 2])
            fig.patch.set_alpha(0.0)
            st.pyplot(fig, transparent=True)
