import streamlit as st
import awswrangler as wr
import boto3
import pandas as pd
import plotly.express as px
import random
import numpy as np
import os as os

# --- COLE ISSO LOGO APÓS OS IMPORTS PARA TESTAR O ACESSO A AWS---
#import streamlit as st
#st.write("Diretório atual:", os.getcwd())
#st.write("Secrets encontrados:", st.secrets.keys() if hasattr(st, "secrets") else "Nenhum")
#if hasattr(st, "secrets") and "aws" in st.secrets:
 #   st.success("A chave [aws] foi lida!")
##   st.error(" O arquivo secrets.toml não foi lido ou falta a seção [aws].")
# --------------------------------------------------

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILO
# ==============================================================================
st.set_page_config(page_title="Bússola do ENEM - Painel do Educador", layout="wide", page_icon="🧭")

st.markdown("""
<style>
    /* Cards de Métricas */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetric"] label { color: #6c757d !important; font-size: 0.9rem; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #212529 !important; font-weight: 700; }
    
    /* Destaque do Aluno */
    .highlight-card {
        background-color: #e3f2fd;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1976d2;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. METADADOS E REGRAS DE NEGÓCIO
# ==============================================================================
CLUSTER_METADATA = {
    -1: {
        "nome": "Estudantes Ausentes",
        "cor": "#D32F2F",
        "perfil": "Provável vulnerabilidade extrema.",
        "diagnostico": "Alunos em situação de vulnerabilidade extrema, com baixa renda e infraestrutura.",
        "acao": ["Mentoria individual.", "Caderno de erros.", "Materiais offline."],
        "storytelling": "Provável trabalho precoce, com pouco tempo para estudo."
    },
    0: {
        "nome": "Estudantes com Recursos Moderados",
        "cor": "#FBC02D",
        "perfil": "Acesso moderado, desorganizado.",
        "diagnostico": "Falta de método de estudo.",
        "acao": ["Cronograma personalizado.", "Revisão semanal.", "Checklists de metas."],
        "storytelling": "Tem recursos básicos, mas ainda não criou o hábito de estudos."
    },
    1: {
        "nome": "Estudantes com Potencial Acadêmico",
        "cor": "#F57C00",
        "perfil": "Alunos dedicados, práticas ineficientes.",
        "diagnostico": "Ineficiência no aprendizado (plateau).",
        "acao": ["Técnica Pomodoro.", "Correção de redação.", "Mentoria em grupo."],
        "storytelling": "Dedicado, mas o desempenho travou por falta de método."
    },
    2: {
        "nome": "Estudantes Disciplinados (Baixa Infra)",
        "cor": "#7B1FA2",
        "perfil": "Baixa infra, alto esforço.",
        "diagnostico": "Necessidade de autonomia.",
        "acao": ["Aulas de nivelamento.", "Simulados progressivos.", "Projetos interdisciplinares."],
        "storytelling": "Resiliente, tende a superar as estatísticas."
    },
    3: {
        "nome": "Estudantes com Forte Base Familiar",
        "cor": "#1976D2",
        "perfil": "Alto potencial, pressão emocional.",
        "diagnostico": "Oscilação emocional.",
        "acao": ["Gestão emocional.", "Rodas de conversa.", "Simulados do ENEM."],
        "storytelling": "Pressão familiar pela expectativa de alto desempenho."
    },
    4: {
        "nome": "Estudantes com Alto Rendimento",
        "cor": "#388E3C",
        "perfil": "Desempenho muito bom.",
        "diagnostico": "Pode sofrer com falta de foco.",
        "acao": ["Aprendizado por projetos.", "Olimpíadas científicas.", "Monitoria."],
        "storytelling": "Engajamento complexo, precisa de desafios."
    }
}

# Gera legendas automáticas para o filtro (Ex: "0 - Estudantes...")
LABELS_FILTRO = {k: f"{k} - {v['nome']}" for k, v in CLUSTER_METADATA.items()}

# ==============================================================================
# 3. CONEXÃO DE DADOS (AWS S3 + PARQUET)
# ==============================================================================

def gerar_dados_ficticios(n=150):
    """Gera dados falsos para demonstração se a AWS falhar."""
    dados = []
    materias = ["Matemática", "Redação", "Ciências da Natureza", "Linguagens", "Humanas"]
    for _ in range(n):
        cluster = random.choices(list(CLUSTER_METADATA.keys()), weights=[5, 15, 20, 20, 25, 15], k=1)[0]
        base_score = 400 + (cluster * 100) if cluster != -1 else 350
        nota = int(max(0, min(1000, np.random.normal(base_score, 60))))
        
        dados.append({
            "id_ra": random.randint(100000, 999999),
            "cluster": cluster,
            "nota_projetada": nota,
            "nome": f"Estudante Anônimo {random.randint(1, 999)}",
            "ponto_fraco": random.choice(materias)
        })
    return pd.DataFrame(dados)

def get_aws_session():
    """Tenta criar sessão AWS via secrets do Streamlit."""
    try:
        if hasattr(st, "secrets") and "aws" in st.secrets:
             return boto3.Session(
                AWS_ACCESS_KEY_ID =st.secrets["aws"]["AWS_ACCESS_KEY_ID"],
                AWS_SECRET_ACCESS_KEY =st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"],
                aws_session_token=st.secrets["aws"].get("aws_session_token"),
                REGION_NAME =st.secrets["aws"]["REGION_NAME"]
            )
    except Exception:
        return None
    return None

@st.cache_data(ttl=600, show_spinner=False)
def load_data():
    """Lê o dataset Parquet particionado do S3."""
    session = get_aws_session()
    
    # 1. Fallback: Se não tem senha, carrega Demo
    if not session:
        return gerar_dados_ficticios(), "⚠️ Modo Demo (Sem credenciais AWS)"

    try:
        # Apontamos para a PASTA RAIZ da versão.
        # O awswrangler entende 'dataset=True' e varre as subpastas (date=...)
        path = "s3://datalake-educacao-handson/gold/app_aluno_scored/v1/"
        
        df = wr.s3.read_parquet(path=path, dataset=True, boto3_session=session)
        
        # 2. Lógica de Data: Pega sempre a carga mais recente
        if 'date' in df.columns:
            latest_date = df['date'].max()
            df = df[df['date'] == latest_date]

        # 3. Renomear colunas técnicas para amigáveis
        mapa = {
            "id_ra_aluno": "id_ra", 
            "cluster_pred": "cluster", 
            "score_norm_pred": "nota_projetada"
        }
        df = df.rename(columns=mapa)
        
        # 4. Tratamento de Tipos e Nulos
        if 'cluster' in df.columns: 
            df['cluster'] = df['cluster'].fillna(0).astype(int)
        
        if 'nota_projetada' in df.columns:
            df['nota_projetada'] = df['nota_projetada'].fillna(0)
            # Normaliza escala se vier 0-100 para 0-1000
            if df['nota_projetada'].max() <= 100: 
                df['nota_projetada'] *= 10
            df['nota_projetada'] = df['nota_projetada'].astype(int)
            
        # 5. Enriquecimento (Se colunas não existirem no parquet, cria fictícias para não quebrar a tela)
        if 'nome' not in df.columns: 
            df['nome'] = df['id_ra'].apply(lambda x: f"Estudante {str(x)[-4:]}")
        if 'ponto_fraco' not in df.columns: 
            materias = ["Matemática", "Redação", "Ciências", "Linguagens"]
            df['ponto_fraco'] = [random.choice(materias) for _ in range(len(df))]
            
        return df, None

    except Exception as e:
        # Se der erro (ex: bucket vazio ou erro de permissão), carrega Demo
        return gerar_dados_ficticios(), f"⚠️ Modo Demo (Erro AWS: {str(e)})"

# ==============================================================================
# 4. INTERFACE E DASHBOARD
# ==============================================================================

# Carregamento
with st.spinner('Conectando ao Data Lake...'):
    df_raw, warning_msg = load_data()

if warning_msg:
    st.toast(warning_msg, icon="⚠️")

# --- SIDEBAR (Filtros) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Seta_bussola.svg/1200px-Seta_bussola.svg.png", width=50) 
    st.title("🏫 Filtros")
    
    # Busca clusters existentes nos dados
    clusters_disp = sorted(df_raw['cluster'].unique())
    
    # Cria o multiselect usando as legendas do dicionário
    sel_cluster = st.multiselect(
        "Perfil:", 
        options=clusters_disp, 
        default=clusters_disp, 
        format_func=lambda x: LABELS_FILTRO.get(x, f"Cluster {x}")
    )
    
    # Aplica filtro
    df_filtered = df_raw[df_raw['cluster'].isin(sel_cluster)]
    
    st.markdown("---")
    st.info(f"Alunos Filtrados: {len(df_filtered)}")
    st.caption(f"Status: {'🟢 Online S3' if not warning_msg else '🟠 Offline/Demo'}")

# --- DASHBOARD PRINCIPAL ---
st.title("🎓 Bússola do ENEM")
st.markdown("### Visão Estratégica dos Alunos")

# 1. KPIs
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

media_nota = df_filtered['nota_projetada'].mean() if not df_filtered.empty else 0
alunos_risco = len(df_filtered[df_filtered['cluster'] <= 0])
cluster_dom = df_filtered['cluster'].mode()[0] if not df_filtered.empty else None
nome_cluster_dom = CLUSTER_METADATA.get(cluster_dom, {}).get('nome', '-')

kpi1.metric("Total de Alunos", len(df_filtered))
kpi2.metric("Nota Média Projetada", f"{media_nota:.0f}", delta=f"{media_nota-700:.0f} vs Meta")
kpi3.metric("Alunos em Risco", alunos_risco, delta_color="inverse")
kpi4.metric("Perfil Predominante", nome_cluster_dom)

st.divider()

# 2. Gráficos e Tabelas
col_grafico, col_lista = st.columns([1, 2])

with col_grafico:
    st.subheader("Distribuição por Perfil")
    if not df_filtered.empty:
        # Prepara dados para o gráfico de rosca
        counts = df_filtered['cluster'].value_counts().reset_index()
        counts.columns = ['cluster', 'count']
        counts['Nome'] = counts['cluster'].map(lambda x: CLUSTER_METADATA.get(x, {}).get('nome'))
        counts['Cor'] = counts['cluster'].map(lambda x: CLUSTER_METADATA.get(x, {}).get('cor'))
        
        fig = px.pie(
            counts, 
            values='count', 
            names='Nome', 
            color='Nome', 
            hole=0.5,
            color_discrete_map={r['Nome']: r['Cor'] for _, r in counts.iterrows()}
        )
        fig.update_layout(showlegend=False, margin=dict(t=20,b=20,l=20,r=20), height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Sem dados para exibir.")

with col_lista:
    st.subheader("Lista de Estudantes")
    
    # Prepara DF para exibição (apenas colunas relevantes)
    df_display = df_filtered[['id_ra', 'nome', 'cluster', 'nota_projetada', 'ponto_fraco']].copy()
    df_display['Perfil'] = df_display['cluster'].map(lambda x: CLUSTER_METADATA.get(x, {}).get('nome'))
    
    # Tabela Interativa
    event = st.dataframe(
        df_display[['id_ra', 'nome', 'Perfil', 'nota_projetada', 'ponto_fraco']],
        column_config={
            "nota_projetada": st.column_config.ProgressColumn(
                "Nota Prevista", format="%d", min_value=0, max_value=1000
            ),
            "id_ra": st.column_config.TextColumn("Matrícula"),
        },
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        height=350
    )

# --- DETALHE DO ALUNO (DRILL DOWN) ---
if len(event.selection.rows) > 0:
    idx = event.selection.rows[0]
    aluno = df_display.iloc[idx]
    meta = CLUSTER_METADATA.get(aluno['cluster'], {})
    
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        # Header do Card
        st.markdown(f"""
        <div class='highlight-card'>
            <h3 style='margin:0'>👤 Análise Individual: {aluno['nome']} (RA: {aluno['id_ra']})</h3>
        </div>
        """, unsafe_allow_html=True)
        
        c_detalhe1, c_detalhe2 = st.columns([1, 2])
        
        with c_detalhe1:
            st.markdown(f"**Perfil Identificado:**")
            st.caption(f"{meta.get('nome')}")
            
            st.markdown("**Desempenho Projetado:**")
            st.progress(aluno['nota_projetada']/1000, text=f"{aluno['nota_projetada']} pontos")
            
            st.markdown("**Ponto de Atenção:**")
            st.warning(f"⚠️ {aluno['ponto_fraco']}")
        
        with c_detalhe2:
            tab_diag, tab_acao = st.tabs(["🩺 Diagnóstico Pedagógico", "🚀 Plano de Ação Sugerido"])
            
            with tab_diag:
                st.markdown("#### Contexto")
                st.info(f"_{meta.get('storytelling')}_")
                st.markdown(f"**Cenário Atual:** {meta.get('perfil')}")
                st.markdown(f"**Diagnóstico:** {meta.get('diagnostico')}")
            
            with tab_acao:
                st.success("Recomendações do Sistema Bússola:")
                acoes = meta.get('acao', [])
                for i, acao in enumerate(acoes):
                    st.checkbox(acao, key=f"check_{aluno['id_ra']}_{i}")