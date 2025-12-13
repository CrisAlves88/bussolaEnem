import streamlit as st
import pandas as pd
import plotly.express as px
import random

# ==============================================================================
# 1. CONFIGURAÇÃO DE PÁGINA E ESTILOS
# ==============================================================================
st.set_page_config(page_title="Bússola do ENEM - Painel do Educador", layout="wide", page_icon="🧭")

st.markdown("""
<style>
    div[data-testid="stMetric"] { background-color: #ffffff !important; border: 1px solid #e0e0e0; }
    div[data-testid="stMetric"] label { color: #666666 !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #222222 !important; }
    .cluster-badge { padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. METADADOS DOS CLUSTERS (Regras de Negócio)
# ==============================================================================
CLUSTER_METADATA = {
    -1: {
        "nome": "Brasil Profundo", "cor": "#D32F2F", 
        "perfil": "Vulnerabilidade extrema.", "acao": ["Materiais impressos", "Busca ativa"],
        "diagnostico": "Dificuldades básicas e instabilidade.", 
        "storytelling": "Provável trabalho precoce ou responsabilidades familiares."
    },
    0: {
        "nome": "Classe Média Tradicional", "cor": "#FBC02D", 
        "perfil": "Acesso moderado, desorganizado.", "acao": ["Técnicas de prova", "Checklists"],
        "diagnostico": "Falta método. Erra questões fáceis.", 
        "storytelling": "Tem recursos básicos, mas sem hábito de estudo."
    },
    1: {
        "nome": "O Lutador", "cor": "#F57C00", 
        "perfil": "Esforço alto, estuda errado.", "acao": ["Pomodoro", "Laboratório Redação"],
        "diagnostico": "Estuda por repetição.", 
        "storytelling": "Dedicado, mas o desempenho trava."
    },
    2: {
        "nome": "Guerreiro (Baixa Infra)", "cor": "#7B1FA2", 
        "perfil": "Pouca posse, alto desempenho.", "acao": ["Bolsas", "Simulados"],
        "diagnostico": "Autonomia alta.", 
        "storytelling": "Resiliente. Faz muito com pouco."
    },
    3: {
        "nome": "Elite Estruturada", "cor": "#1976D2", 
        "perfil": "Recursos altos, ansiedade.", "acao": ["Gestão emocional", "Debates"],
        "diagnostico": "Oscilação emocional.", 
        "storytelling": "Suporte familiar, mas trava sob pressão."
    },
    4: {
        "nome": "Super-Elite", "cor": "#388E3C", 
        "perfil": "Topo desempenho.", "acao": ["PBL", "Olimpíadas"],
        "diagnostico": "Falta propósito.", 
        "storytelling": "Desafio é manter engajamento."
    }
}

# ==============================================================================
# 3. LEITURA DE DADOS (MODO ARQUIVO LOCAL - SEM AWS)
# ==============================================================================
@st.cache_data
def load_data():
    try:
        # Tenta ler o arquivo CSV que você baixou
        df = pd.read_csv("dados_gold.csv")
        
        # AJUSTE DE COLUNAS (DE-PARA)
        # O CSV da gold geralmente vem com nomes técnicos, vamos padronizar:
        # Tenta identificar colunas comuns e renomear
        cols_map = {
            "id_ra_aluno": "id_ra",
            "cluster": "cluster",
            "nota_prevista": "nota_projetada",
            "nota_projetada": "nota_projetada", # Caso já venha certo
            "frequencia": "frequencia",
            "ponto_fraco": "ponto_fraco"
        }
        df = df.rename(columns=cols_map)
        
        # Garante que as colunas existem (se não existirem no CSV, cria fake)
        if "id_ra" not in df.columns: df["id_ra"] = [f"2024{i}" for i in range(len(df))]
        if "cluster" not in df.columns: df["cluster"] = [random.choice([0,1,2]) for _ in range(len(df))]
        if "nota_projetada" not in df.columns: df["nota_projetada"] = [random.randint(400,800) for _ in range(len(df))]
        if "frequencia" not in df.columns: df["frequencia"] = [random.randint(70,100) for _ in range(len(df))]
        if "ponto_fraco" not in df.columns: df["ponto_fraco"] = [random.choice(["Matemática", "Redação"]) for _ in range(len(df))]

        # Limpeza de tipos
        df['cluster'] = df['cluster'].fillna(0).astype(int)
        df['nota_projetada'] = df['nota_projetada'].fillna(0).astype(int)
        
        # Cria nome fake se não tiver
        if 'nome' not in df.columns:
            df['nome'] = df['id_ra'].apply(lambda x: f"Estudante {str(x)[-4:]}")
            
        return df, None

    except FileNotFoundError:
        return None, "Arquivo 'dados_gold.csv' não encontrado. Faça o upload dele para a pasta."
    except Exception as e:
        return None, f"Erro ao ler CSV: {str(e)}"

# Carrega os dados
df_raw, error = load_data()

# ==============================================================================
# 4. INTERFACE DO DASHBOARD
# ==============================================================================
if error:
    st.error("❌ ERRO: Precisamos do arquivo de dados.")
    st.warning(f"Detalhe: {error}")
    st.info("💡 Solução: Baixe o CSV da URL que você tem, renomeie para 'dados_gold.csv' e arraste para a pasta deste projeto.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("🏫 Filtros")
    clusters_sel = st.multiselect("Perfil:", options=sorted(df_raw['cluster'].unique()), default=sorted(df_raw['cluster'].unique()))
    df_filtered = df_raw[df_raw['cluster'].isin(clusters_sel)]
    st.write(f"Alunos: {len(df_filtered)}")

# --- MAIN ---
st.title("🧭 Bússola do ENEM")

c1, c2, c3 = st.columns(3)
c1.metric("Média Turma", f"{df_filtered['nota_projetada'].mean():.0f}")
c2.metric("Total Alunos", len(df_filtered))
c3.metric("Risco (Cluster -1)", len(df_filtered[df_filtered['cluster'] == -1]))

st.divider()

c_chart, c_table = st.columns([1, 2])

with c_chart:
    st.subheader("Distribuição")
    counts = df_filtered['cluster'].value_counts().reset_index()
    counts['Nome'] = counts['cluster'].map(lambda x: CLUSTER_METADATA.get(x, {}).get('nome'))
    counts['Cor'] = counts['cluster'].map(lambda x: CLUSTER_METADATA.get(x, {}).get('cor', '#ccc'))
    fig = px.pie(counts, values='count', names='Nome', color='Nome', 
                 color_discrete_map={r['Nome']: r['Cor'] for _, r in counts.iterrows()})
    fig.update_layout(showlegend=False, height=250, margin=dict(t=0,b=0,l=0,r=0))
    st.plotly_chart(fig, use_container_width=True)

with c_table:
    st.subheader("Lista de Alunos")
    df_show = df_filtered.copy()
    df_show['Perfil'] = df_show['cluster'].map(lambda x: CLUSTER_METADATA.get(x, {}).get('nome'))
    
    selection = st.dataframe(
        df_show[['id_ra', 'nome', 'Perfil', 'nota_projetada', 'ponto_fraco']],
        column_config={"nota_projetada": st.column_config.ProgressColumn("Nota", format="%d", min_value=0, max_value=1000)},
        use_container_width=True, hide_index=True, selection_mode="single-row", on_select="rerun", height=300
    )

if selection.selection.rows:
    aluno = df_show.iloc[selection.selection.rows[0]]
    meta = CLUSTER_METADATA.get(aluno['cluster'], {})
    
    st.divider()
    st.header(f"👤 {aluno['nome']}")
    
    col_l, col_r = st.columns([1, 3])
    with col_l:
        st.markdown(f"""
        <div style="background:{meta.get('cor')}; padding:15px; border-radius:10px; color:white; text-align:center;">
            <h1>{aluno['nota_projetada']}</h1>
            <p>{meta.get('nome')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_r:
        t1, t2 = st.tabs(["Diagnóstico", "Plano de Ação"])
        with t1:
            st.write(f"_{meta.get('storytelling')}_")
            st.info(meta.get('diagnostico'))
        with t2:
            for acao in meta.get('acao', []):
                st.checkbox(acao, key=acao)