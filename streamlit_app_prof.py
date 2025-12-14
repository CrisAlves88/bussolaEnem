import streamlit as st
import awswrangler as wr
import boto3
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
    -1: {"nome": "Brasil Profundo", "cor": "#D32F2F", "perfil": "Vulnerabilidade extrema.", "diagnostico": "Dificuldades básicas.", "acao": ["Materiais impressos", "Busca ativa"], "storytelling": "Provável trabalho precoce."},
    0: {"nome": "Classe Média Tradicional", "cor": "#FBC02D", "perfil": "Acesso moderado, desorganizado.", "diagnostico": "Falta método.", "acao": ["Técnicas de prova", "Checklists"], "storytelling": "Recursos básicos, sem hábito."},
    1: {"nome": "O Lutador", "cor": "#F57C00", "perfil": "Esforço alto, estuda errado.", "diagnostico": "Repetição.", "acao": ["Pomodoro", "Redação"], "storytelling": "Dedicado, desempenho trava."},
    2: {"nome": "Guerreiro (Baixa Infra)", "cor": "#7B1FA2", "perfil": "Pouca posse, alto desempenho.", "diagnostico": "Autonomia.", "acao": ["Bolsas", "Simulados"], "storytelling": "Resiliente."},
    3: {"nome": "Elite Estruturada", "cor": "#1976D2", "perfil": "Recursos altos, ansiedade.", "diagnostico": "Oscilação emocional.", "acao": ["Gestão emocional"], "storytelling": "Pressão familiar."},
    4: {"nome": "Super-Elite", "cor": "#388E3C", "perfil": "Topo desempenho.", "diagnostico": "Falta propósito.", "acao": ["PBL", "Olimpíadas"], "storytelling": "Engajamento complexo."}
}

# ==============================================================================
# 3. CONEXÃO AWS E LEITURA (AJUSTADA PARA O SEU CSV)
# ==============================================================================
def get_aws_session():
    # Tenta pegar as credenciais do secrets.toml ou do ambiente
    try:
        if hasattr(st, "secrets") and "aws" in st.secrets:
             return boto3.Session(
                aws_access_key_id=st.secrets["aws"]["aws_access_key_id"],
                aws_secret_access_key=st.secrets["aws"]["aws_secret_access_key"],
                aws_session_token=st.secrets["aws"].get("aws_session_token"),
                region_name=st.secrets["aws"]["region_name"]
            )
        elif 'AWS_ACCESS_KEY_ID' in st.secrets:
            return boto3.Session(
                aws_access_key_id=st.secrets['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=st.secrets['AWS_SECRET_ACCESS_KEY'],
                region_name=st.secrets.get('AWS_DEFAULT_REGION', 'us-east-1')
            )
    except Exception:
        pass
    return boto3.Session()

@st.cache_data(ttl=600)
def load_data_from_s3():
    session = get_aws_session()
    s3_client = session.client('s3')
    bucket_name = "datalake-educacao-handson"
    prefix = "gold/app_aluno_scored/v1/"
    
    try:
        # Lista os objetos no bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        arquivos = [o['Key'] for o in response.get('Contents', []) if o['Key'].endswith('.csv') and not o['Key'].split('/')[-1].startswith('._')]

        if not arquivos: return None, "Nenhum CSV encontrado."
        
        # Pega o arquivo mais recente
        arquivo_alvo = sorted(arquivos, reverse=True)[0]
        path = f"s3://{bucket_name}/{arquivo_alvo}"
        
        # Lê o CSV
        df = wr.s3.read_csv(path=path, boto3_session=session, encoding='latin1', sep=',', on_bad_lines='skip')
        
        # --- CORREÇÃO DE COLUNAS (Baseado no seu arquivo) ---
        # Mapeamento exato das colunas do seu arquivo para o app
        mapa_colunas = {
            "id_ra_aluno": "id_ra",
            "cluster_pred": "cluster",      # AQUI ESTAVA O ERRO (era 'cluster_pred')
            "score_norm_pred": "nota_projetada",
            "created_at": "date"
        }
        df = df.rename(columns=mapa_colunas)
        
        # --- TRATAMENTO DE DADOS ---
        
        # 1. Garante que 'cluster' existe e é inteiro
        if 'cluster' in df.columns:
            df['cluster'] = df['cluster'].fillna(0).astype(int)
        else:
            return None, f"Coluna 'cluster_pred' não encontrada. Colunas no arquivo: {df.columns.tolist()}"

        # 2. Ajusta a nota para escala ENEM (0-1000) se estiver em 0-100
        if 'nota_projetada' in df.columns:
            df['nota_projetada'] = df['nota_projetada'].fillna(0)
            if df['nota_projetada'].max() <= 100:
                df['nota_projetada'] = df['nota_projetada'] * 10
            df['nota_projetada'] = df['nota_projetada'].astype(int)
        
        # 3. Cria colunas fictícias que faltam no arquivo original
        if 'nome' not in df.columns: 
            df['nome'] = df['id_ra'].apply(lambda x: f"Estudante {str(x)[-4:]}")
        
        if 'ponto_fraco' not in df.columns: 
            df['ponto_fraco'] = [random.choice(["Matemática", "Redação", "Ciências da Natureza"]) for _ in range(len(df))]

        return df, None

    except Exception as e:
        return None, str(e)

# ==============================================================================
# 4. CARREGAMENTO
# ==============================================================================
with st.spinner('Conectando AWS S3...'):
    df_raw, error = load_data_from_s3()

if error:
    st.error(f"Erro ao carregar dados: {error}")
    st.stop()

if df_raw is None or df_raw.empty:
    st.warning("Tabela vazia ou erro na leitura.")
    st.stop()

# ==============================================================================
# 5. DASHBOARD
# ==============================================================================
with st.sidebar:
    st.title("🏫 Filtros")
    
    # Filtro de Cluster
    clusters_disp = sorted(df_raw['cluster'].unique())
    sel_cluster = st.multiselect("Perfil:", options=clusters_disp, default=clusters_disp, format_func=lambda x: f"CL {x}")
    
    # Filtro de Dados
    df_filtered = df_raw[df_raw['cluster'].isin(sel_cluster)]
    
    st.markdown("---")
    st.info(f"Alunos Filtrados: {len(df_filtered)}")
    st.caption("Conectado via AWS S3 Gold Layer")

st.title("🎓 Bússola do ENEM")

# Métricas Principais
c1, c2, c3 = st.columns(3)
media_nota = df_filtered['nota_projetada'].mean()
c1.metric("Nota Média Projetada", f"{media_nota:.0f}", delta="Meta: 700")
c2.metric("Total de Alunos", len(df_filtered))
c3.metric("Alunos em Risco (CL -1/0)", len(df_filtered[df_filtered['cluster'] <= 0]))

st.divider()

col_graf, col_tab = st.columns([1, 2])

with col_graf:
    st.subheader("Distribuição por Perfil")
    counts = df_filtered['cluster'].value_counts().reset_index()
    counts.columns = ['cluster', 'count']
    counts['Nome'] = counts['cluster'].map(lambda x: CLUSTER_METADATA.get(x, {}).get('nome', f'Cluster {x}'))
    counts['Cor'] = counts['cluster'].map(lambda x: CLUSTER_METADATA.get(x, {}).get('cor', '#ccc'))
    
    fig = px.pie(counts, values='count', names='Nome', color='Nome', 
                 color_discrete_map={r['Nome']: r['Cor'] for _, r in counts.iterrows()})
    fig.update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0), height=250)
    st.plotly_chart(fig, use_container_width=True)

with col_tab:
    st.subheader("Lista de Estudantes")
    df_show = df_filtered.copy()
    df_show['Perfil'] = df_show['cluster'].map(lambda x: CLUSTER_METADATA.get(x, {}).get('nome'))
    
    selection = st.dataframe(
        df_show[['id_ra', 'nome', 'Perfil', 'nota_projetada', 'ponto_fraco']],
        column_config={
            "nota_projetada": st.column_config.ProgressColumn("Nota (0-1000)", format="%d", min_value=0, max_value=1000),
            "id_ra": st.column_config.TextColumn("RA"),
        },
        use_container_width=True, hide_index=True, selection_mode="single-row", on_select="rerun", height=300
    )

# Detalhe do Aluno
if selection.selection.rows:
    aluno = df_show.iloc[selection.selection.rows[0]]
    meta = CLUSTER_METADATA.get(aluno['cluster'], {})
    st.divider()
    st.header(f"👤 {aluno['nome']} (RA: {aluno['id_ra']})")
    
    cL, cR = st.columns([1,3])
    with cL:
        st.markdown(f"""
        <div style='background:{meta.get('cor')};padding:20px;border-radius:10px;color:white;text-align:center'>
            <h1>{aluno['nota_projetada']}</h1>
            <p>Nota Projetada</p>
            <hr style="border-color:rgba(255,255,255,0.3)">
            <strong>{meta.get('nome')}</strong>
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"Ponto de Atenção: {aluno['ponto_fraco']}")
        
    with cR:
        t1, t2 = st.tabs(["Diagnóstico", "Plano de Ação"])
        with t1: 
            st.info(meta.get('diagnostico'))
            st.write(f"_{meta.get('storytelling')}_")
        with t2: 
            st.write("SUGESTÕES DE INTERVENÇÃO:")
            for a in meta.get('acao', []): st.checkbox(a)