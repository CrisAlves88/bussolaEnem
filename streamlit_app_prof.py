import streamlit as st
import awswrangler as wr
import boto3
import pandas as pd
import plotly.express as px
import random
import numpy as np

# ==============================================================================
# 1. CONFIGURAÇÃO DE PÁGINA E ESTILOS
# ==============================================================================
st.set_page_config(page_title="Bússola do ENEM - Painel do Educador", layout="wide", page_icon="🧭")

st.markdown("""
<style>
    /* Estilo dos Cards de Métricas */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetric"] label { color: #6c757d !important; font-size: 0.9rem; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #212529 !important; font-weight: 700; }
    
    /* Cabeçalho de Seleção */
    .highlight-card {
        background-color: #e3f2fd;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1976d2;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. METADADOS DOS CLUSTERS (Regras de Negócio e Cores)
# ==============================================================================
CLUSTER_METADATA = {
    -1: {
        "nome": "Estudantes Ausentes",
        "cor": "#D32F2F",
        "perfil": "Provável vulnerabilidade extrema.",
        "diagnostico": "Alunos em situação de vulnerabilidade extrema, com baixa renda e infraestrutura.",
        "acao": [
            "Mentoria individual com rotinas de leitura diária guiada.",
            "Caderno de erros e resolução comentada do ENEM.",
            "Materiais offline (impressos, jogos pedagógicos)."
        ],
        "storytelling": "Provável trabalho precoce, com pouco tempo para estudo."
    },
    0: {
        "nome": "Estudantes com Recursos Moderados",
        "cor": "#FBC02D",
        "perfil": "Acesso moderado, desorganizado.",
        "diagnostico": "Falta de método de estudo.",
        "acao": [
            "Cronograma de estudos personalizado.",
            "Revisão semanal focada em erros frequentes.",
            "Checklists de metas atingidas.",
            "Listas de exercícios graduais."
        ],
        "storytelling": "Tem recursos básicos, mas ainda não criou o hábito de estudos."
    },
    1: {
        "nome": "Estudantes com Potencial Acadêmico",
        "cor": "#F57C00",
        "perfil": "Alunos dedicados, mas com práticas de estudo ineficientes.",
        "diagnostico": "Ineficiência no aprendizado (plateau).",
        "acao": [
            "Ensino de organização do estudo (Técnica Pomodoro).",
            "Correção de redação.",
            "Mentoria em grupo com alunos do mesmo perfil."
        ],
        "storytelling": "Muito dedicado, mas o desempenho travou por falta de método e organização dos estudos."
    },
    2: {
        "nome": "Estudantes Disciplinados (Baixa Infra)",
        "cor": "#7B1FA2",
        "perfil": "Baixa infraestrutura, mas bom desempenho e alto esforço.",
        "diagnostico": "Necessidade de autonomia.",
        "acao": [
            "Aulas curtas de nivelamento.",
            "Simulados semanais com progressão na dificuldade.",
            "Projetos interdisciplinares."
        ],
        "storytelling": "Resiliente, tende a superar as estatísticas."
    },
    3: {
        "nome": "Estudantes com Forte Base Familiar",
        "cor": "#1976D2",
        "perfil": "Alto potencial, mas pressão emocional.",
        "diagnostico": "Possível oscilação emocional devido à expectativa de bom desempenho.",
        "acao": [
            "Gestão emocional.",
            "Rodas de conversa sobre as dificuldades dos alunos.",
            "Grupos de estudos supervisionados.",
            "Simulados do ENEM."
        ],
        "storytelling": "Pressão familiar pela expectativa de alto desempenho."
    },
    4: {
        "nome": "Estudantes com Alto Rendimento e Boa Estrutura",
        "cor": "#388E3C",
        "perfil": "Desempenho muito bom.",
        "diagnostico": "Ótimo desempenho, mas pode sofrer com falta de foco.",
        "acao": [
            "Aprendizado por projetos.",
            "Participação em olimpíadas científicas.",
            "Desafios fora da sala de aula.",
            "Potencial para ser monitor de grupos pequenos."
        ],
        "storytelling": "Engajamento complexo, precisa de desafios."
    }
}

# ==============================================================================
# 3. FUNÇÕES DE DADOS (COM FALLBACK PARA DEMO)
# ==============================================================================

def gerar_dados_ficticios(n=150):
    """Gera dados simulados caso a AWS falhe (Modo Demonstração)"""
    dados = []
    materias = ["Matemática", "Redação", "Ciências da Natureza", "Linguagens", "Humanas"]
    
    for _ in range(n):
        # Pesos para garantir que apareçam todos os clusters
        cluster = random.choices(list(CLUSTER_METADATA.keys()), weights=[5, 15, 20, 20, 25, 15], k=1)[0]
        
        # Nota baseada no cluster (clusters maiores tendem a ter notas maiores na simulação)
        base_score = 400 + (cluster * 100) 
        if cluster == -1: base_score = 350
        
        nota = int(np.random.normal(base_score, 60))
        nota = max(0, min(1000, nota)) # clamp entre 0 e 1000
        
        dados.append({
            "id_ra": random.randint(100000, 999999),
            "cluster": cluster,
            "nota_projetada": nota,
            "nome": f"Estudante Anônimo {random.randint(1, 999)}",
            "ponto_fraco": random.choice(materias)
        })
    return pd.DataFrame(dados)

def get_aws_session():
    try:
        if hasattr(st, "secrets") and "aws" in st.secrets:
             return boto3.Session(
                aws_access_key_id=st.secrets["aws"]["aws_access_key_id"],
                aws_secret_access_key=st.secrets["aws"]["aws_secret_access_key"],
                aws_session_token=st.secrets["aws"].get("aws_session_token"),
                region_name=st.secrets["aws"]["region_name"]
            )
    except Exception:
        return None
    return None

@st.cache_data(ttl=600, show_spinner=False)
def load_data():
    # 1. Tenta conectar na AWS
    session = get_aws_session()
    
    # SE NÃO TIVER CREDENCIAIS, VAI DIRETO PRO MODO DEMO
    if not session:
        return gerar_dados_ficticios(), "⚠️ Modo Demo (Sem credenciais AWS)"

    # 2. Tenta ler do S3
    try:
        bucket_name = "datalake-educacao-handson"
        prefix = "gold/app_aluno_scored/v1/"
        
        s3_client = session.client('s3')
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        arquivos = [o['Key'] for o in response.get('Contents', []) if o['Key'].endswith('.csv')]

        if not arquivos:
            return gerar_dados_ficticios(), "⚠️ Modo Demo (Nenhum CSV no bucket)"
        
        arquivo_alvo = sorted(arquivos, reverse=True)[0]
        path = f"s3://{bucket_name}/{arquivo_alvo}"
        
        df = wr.s3.read_csv(path=path, boto3_session=session, encoding='latin1', sep=',', on_bad_lines='skip')
        
        # Renomeia colunas
        mapa = {"id_ra_aluno": "id_ra", "cluster_pred": "cluster", "score_norm_pred": "nota_projetada"}
        df = df.rename(columns=mapa)
        
        # Tratamento de Nulos e Tipos
        if 'cluster' in df.columns: df['cluster'] = df['cluster'].fillna(0).astype(int)
        if 'nota_projetada' in df.columns:
            df['nota_projetada'] = df['nota_projetada'].fillna(0)
            if df['nota_projetada'].max() <= 100: df['nota_projetada'] *= 10
            df['nota_projetada'] = df['nota_projetada'].astype(int)
            
        # Criação de colunas auxiliares se não existirem
        if 'nome' not in df.columns: 
            df['nome'] = df['id_ra'].apply(lambda x: f"Estudante {str(x)[-4:]}")
        if 'ponto_fraco' not in df.columns: 
            df['ponto_fraco'] = [random.choice(["Matemática", "Redação", "Ciências"]) for _ in range(len(df))]
            
        return df, None

    except Exception as e:
        # Se der erro na AWS (ex: bucket não existe), retorna fictício + msg de erro
        return gerar_dados_ficticios(), f"⚠️ Modo Demo (Erro AWS: {str(e)})"

# ==============================================================================
# 4. CARREGAMENTO E SIDEBAR (COM AS LEGENDAS NOVAS)
# ==============================================================================
with st.spinner('Carregando dados da Bússola...'):
    df_raw, warning_msg = load_data()

if warning_msg:
    st.toast(warning_msg, icon="⚠️")

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Seta_bussola.svg/1200px-Seta_bussola.svg.png", width=50) 
    st.title("🏫 Filtros")
    
    # --- MAPEAMENTO DE LEGENDAS DO FILTRO (O QUE VOCÊ PEDIU) ---
    LABELS_FILTRO = {
        -1: "-1 - Estudantes ausentes", # Mantive caso apareça nos dados
        0: "0 - Estudantes com recursos moderados",
        1: "1 - Estudantes com potencial acadêmico",
        2: "2 - Estudantes disciplinados com baixa infraestrutura",
        3: "3 - Estudantes com forte base familiar",
        4: "4 - Estudantes com alto rendimento e boa estrutura"
    }
    
    clusters_disp = sorted(df_raw['cluster'].unique())
    
    # Multiselect com format_func usando o dicionário acima
    sel_cluster = st.multiselect(
        "Perfil:", 
        options=clusters_disp, 
        default=clusters_disp, 
        format_func=lambda x: LABELS_FILTRO.get(x, f"CL {x}") # Busca a legenda, se não achar usa 'CL X'
    )
    
    df_filtered = df_raw[df_raw['cluster'].isin(sel_cluster)]
    
    st.markdown("---")
    st.info(f"Alunos Filtrados: {len(df_filtered)}")
    st.caption(f"Status: {'🟢 Online S3' if not warning_msg else '🟠 Offline/Demo'}")

# ==============================================================================
# 5. DASHBOARD PRINCIPAL
# ==============================================================================
st.title("🎓 Bússola do ENEM")
st.markdown("Visão Geral do Desempenho dos Estudantes")

# KPIs
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
media_nota = df_filtered['nota_projetada'].mean() if not df_filtered.empty else 0
risco = len(df_filtered[df_filtered['cluster'] <= 0])

kpi1.metric("Alunos Monitorados", len(df_filtered))
kpi2.metric("Nota Média (Geral)", f"{media_nota:.0f}", delta=f"{media_nota-700:.0f} vs Meta")
kpi3.metric("Em Risco (Alta Vulnerabilidade)", risco, delta_color="inverse")
kpi4.metric("Cluster Dominante", CLUSTER_METADATA.get(df_filtered['cluster'].mode()[0], {}).get('nome', '-') if not df_filtered.empty else "-")

st.divider()

# Gráficos e Tabela
c_charts, c_list = st.columns([1, 2])

with c_charts:
    st.subheader("Distribuição")
    if not df_filtered.empty:
        counts = df_filtered['cluster'].value_counts().reset_index()
        counts.columns = ['cluster', 'count']
        counts['Nome'] = counts['cluster'].map(lambda x: CLUSTER_METADATA.get(x, {}).get('nome'))
        counts['Cor'] = counts['cluster'].map(lambda x: CLUSTER_METADATA.get(x, {}).get('cor'))
        
        fig = px.pie(counts, values='count', names='Nome', color='Nome', hole=0.4,
                     color_discrete_map={r['Nome']: r['Cor'] for _, r in counts.iterrows()})
        fig.update_layout(showlegend=False, margin=dict(t=10,b=10,l=10,r=10), height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados para exibir gráfico.")

with c_list:
    st.subheader("Lista de Alunos")
    
    # Preparando dataframe para exibição
    df_display = df_filtered[['id_ra', 'nome', 'cluster', 'nota_projetada', 'ponto_fraco']].copy()
    df_display['Perfil'] = df_display['cluster'].map(lambda x: CLUSTER_METADATA.get(x, {}).get('nome'))
    
    event = st.dataframe(
        df_display[['id_ra', 'nome', 'Perfil', 'nota_projetada', 'ponto_fraco']],
        column_config={
            "nota_projetada": st.column_config.ProgressColumn("Nota Prevista", format="%d", min_value=0, max_value=1000),
            "id_ra": st.column_config.TextColumn("Matrícula"),
        },
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        height=300
    )

# Detalhe do Aluno Selecionado
if len(event.selection.rows) > 0:
    idx = event.selection.rows[0]
    aluno = df_display.iloc[idx]
    meta = CLUSTER_METADATA.get(aluno['cluster'], {})
    
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown(f"<div class='highlight-card'><h3>👤 Análise Individual: {aluno['nome']}</h3></div>", unsafe_allow_html=True)
        
        c_det1, c_det2 = st.columns([1, 2])
        
        with c_det1:
            st.markdown(f"**Perfil:** {meta.get('nome')}")
            st.progress(aluno['nota_projetada']/1000, text=f"Nota Projetada: {aluno['nota_projetada']}")
            st.warning(f"⚠️ Ponto de Atenção: {aluno['ponto_fraco']}")
        
        with c_det2:
            tab_diag, tab_acao = st.tabs(["🩺 Diagnóstico", "🚀 Plano de Ação"])
            with tab_diag:
                st.write(f"**Cenário:** {meta.get('perfil')}")
                st.write(f"**Diagnóstico:** {meta.get('diagnostico')}")
                st.info(f"Contexto: \"{meta.get('storytelling')}\"")
            with tab_acao:
                st.success("Recomendações do Sistema:")
                cols = st.columns(len(meta.get('acao', [])))
                for i, acao in enumerate(meta.get('acao', [])):
                    st.checkbox(acao, key=f"acao_{aluno['id_ra']}_{i}")