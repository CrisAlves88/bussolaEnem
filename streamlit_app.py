import streamlit as st
import json
import time
import requests
import string

# Configuração da Página
st.set_page_config(page_title="Bússola ENEM - MVP", layout="centered")

# --- 1. CONFIGURAÇÃO E DICIONÁRIOS DE DADOS (MOCK DO INEP) ---

def get_inep_mappings():
    # Dicionários completos para garantir o De-Para correto
    return {
        # Códigos padrão INEP
        "raca": {"Selecione...": 0, "Não declarado": 0, "Branca": 1, "Preta": 2, "Parda": 3, "Amarela": 4, "Indígena": 5},
        
        "nacionalidade": {
            "Não informado": 0, "Brasileiro(a)": 1, "Brasileiro(a) Naturalizado(a)": 2, 
            "Estrangeiro(a)": 3, "Brasileiro(a) Nato(a), nascido(a) no exterior": 4
        },
        
        # Mapeamento de Faixa Etária (1 a 20)
        "faixa_etaria": {
            "Menor de 17 anos": 1, "17 anos": 2, "18 anos": 3, "19 anos": 4, "20 anos": 5, 
            "21 anos": 6, "22 anos": 7, "23 anos": 8, "24 anos": 9, "25 anos": 10, 
            "entre 26 e 30 anos": 11, "entre 31 e 35": 12, "entre 36 e 40 anos": 13, 
            "entre 41 e 45 anos": 14, "entre 46 e 50 anos": 15, "entre 51 e 55 anos": 16, 
            "entre 56 e 60 anos": 17, "entre 61 e 65 anos": 18, "entre 66 e 70": 19, "Acima de 70 anos": 20
        },
        
        "estado_civil": {
            "Solteiro(a)": 1, "Casado(a)/Mora com um(a) companheiro(a)": 2, 
            "Divorciado(a)/Desquitado(a)/Separado(a)": 3, "Viúvo(a)": 4
        },

        "situacao_em": {
            "Já concluí": 1, "Estou cursando o último ano": 2, "Estou cursando (não concluo este ano)": 3
        },
        
        "dependencia_adm": {"Federal": 1, "Estadual": 2, "Municipal": 3, "Privada": 4},
        
        # Listas para geração de letras (A, B, C...)
        "escolaridade": [
            "Nunca estudou", "Não completou a 4ª série/5º ano do Ensino Fundamental.", 
            "Completou a 4ª série/5º ano, mas não completou a 8ª série/9º ano do Ensino Fundamental.",
            "Completou a 8ª série/9º ano do Ensino Fundamental, mas não completou o Ensino Médio.", 
            "Completou o Ensino Médio, mas não completou a Faculdade.", "Completou a Faculdade, mas não completou a Pós-graduação.", 
            "Completou a Pós-graduação.", "Não sei."
        ],
        
        "renda": [
            "Nenhuma renda.", "Até R$ 788,00.", "De R$ 788,01 até R$ 1.182,00.",
            "De R$ 1.182,01 até R$ 1.572,00.", "De R$ 1.572,01 até R$ 1.970,00.",
            "De R$ 1.970,01 até R$ 2.364,00.", "De R$ 2.364,01 até R$ 3.152,00.",
            "De R$ 3.152,01 até R$ 3.940,00.", "De R$ 3.940,01 até R$ 4.728,00.",
            "De R$ 4.728,01 até R$ 5.516,00.", "De R$ 5.516,01 até R$ 6.304,00.",
            "De R$ 6.304,01 até R$ 7.092,00.", "De R$ 7.092,01 até R$ 7.880,00.",
            "De R$ 7.880,01 até R$ 9.456,00.", "De R$ 9.456,01 até R$ 11.820,00.",
            "De R$ 11.820,01 até R$ 15.760,00.", "Mais de 15.760,00."
        ]       
    }

MAPS = get_inep_mappings()

if 'step' not in st.session_state: st.session_state.step = 1
if 'user_data' not in st.session_state: st.session_state.user_data = {}

# Funções de Navegação
def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# --- 2. COMPONENTES DA UI ---

def render_header():
    st.title("🧭 Bússola do ENEM")
    st.write("Diagnóstico personalizado baseado em dados históricos.")
    progress_map = {1: 0.25, 2: 0.50, 3: 0.75, 4: 1.0}
    st.progress(progress_map.get(st.session_state.step, 1.0))
    st.caption(f"Passo {st.session_state.step} de 4")
    st.markdown("---")

def step_1_identity():
    st.header("1. Queremos te conhecer!")
    st.info("Para identificação única, por favor insira seu Registro Acadêmico (RA).")
    st.session_state.user_data['ra_aluno'] = st.text_input("RA do Aluno", placeholder="Digite seu RA aqui").strip()
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.user_data['idade'] = st.selectbox("Faixa Etária", ["Selecione..."] + list(MAPS['faixa_etaria'].keys())[0:])
        st.session_state.user_data['sexo'] = st.radio("Sexo", ["Masculino", "Feminino"], horizontal=True)
        st.session_state.user_data['nacionalidade'] = st.selectbox("Nacionalidade", ["Selecione..."] + list(MAPS['nacionalidade'].keys()))
    with c2:
        st.session_state.user_data['cor_raca'] = st.selectbox("Cor/Raça", list(MAPS['raca'].keys()))
        # Correção ortográfica realizada: "Solteiro(a)"
        st.session_state.user_data['estado_civil'] = st.selectbox("Estado Civil", ["Selecione..."] + list(MAPS['estado_civil'].keys()))
        st.session_state.user_data['pessoas_casa'] = st.number_input("Pessoas na casa (incluindo você):", min_value=1, step=1)
    st.button("Próximo ➡️", on_click=next_step)

def step_2_school():
    st.header("2. Preencha sobre sua Escola")
    st.session_state.user_data['situacao_em'] = st.radio("Situação do Ensino Médio", list(MAPS['situacao_em'].keys()))
    
    c1, c2 = st.columns(2)
    with c1:
        # Lista de anos ajustada conforme solicitação
        anos = ["Não informado", "2026", "2025", "2024", "2023"]
        st.session_state.user_data['ano_conclusao'] = st.selectbox("Ano de Conclusão", anos)
        st.session_state.user_data['tipo_escola'] = st.selectbox("Tipo de Escola", ["Selecione...", "Pública", "Particular"])
    with c2:
        st.session_state.user_data['uf_escola'] = st.selectbox("Estado (UF)", ["SP", "RJ", "MG", "ES", "RS", "SC", "PR", "BA", "PE", "CE", "AM", "Outro"]) 
        st.session_state.user_data['municipio'] = st.text_input("Município", placeholder="Ex: São Paulo")
    
    st.markdown("##### Detalhes da Instituição")
    st.session_state.user_data['dependencia_adm'] = st.selectbox("Dependência Adm.", ["Selecione..."] + list(MAPS['dependencia_adm'].keys()))
    st.session_state.user_data['localizacao_esc'] = st.radio("Localização", ["Urbana", "Rural"], horizontal=True)
    st.session_state.user_data['certificacao'] = st.checkbox("Solicitei certificação do Ensino Médio pelo Enem?")
    
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1: st.button("⬅️ Voltar", on_click=prev_step)
    with col_nav2: st.button("Próximo ➡️", on_click=next_step)

def step_3_family():
    st.header("3. Contexto Familiar")
    c1, c2 = st.columns(2)
    # Lista auxiliar para grupos de ocupação
    ocups = [
        "Grupo 1 (Lavradores, agricultores sem empregados...)", 
        "Grupo 2 (Diaristas, domésticos, cuidadores...)", 
        "Grupo 3 (Profissionais de produção, metalúrgicos...)", 
        "Grupo 4 (Professores, técnicos, gerentes...)", 
        "Grupo 5 (Médicos, engenheiros, dentistas...)", 
        "Não sei"
    ]
    
    with c1:
        st.session_state.user_data['pai_estudo'] = st.selectbox("Meu pai estudou até:", MAPS['escolaridade'])
        st.session_state.user_data['mae_estudo'] = st.selectbox("Minha mãe estudou até:", MAPS['escolaridade'])
    with c2:
        st.session_state.user_data['pai_ocupacao'] = st.selectbox("Ocupação Pai", ocups)
        st.session_state.user_data['mae_ocupacao'] = st.selectbox("Ocupação Mãe", ocups)
    
    st.markdown("---")
    st.session_state.user_data['renda'] = st.selectbox("Renda Mensal Familiar Total:", options=MAPS['renda'], index=None, placeholder="Selecione a faixa...")
    
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1: st.button("⬅️ Voltar", on_click=prev_step)
    with col_nav2: st.button("Próximo ➡️", on_click=next_step)

def step_4_infrastructure():
    st.header("4. Nos fale sobre sua casa")
    
    # Função auxiliar simples, sem criar colunas internamente
    def item_row(label, key):
        return st.selectbox(label, ["Não tem"]+[str(i) for i in range(1,4)]+["4+"], key=key)

    c1, c2 = st.columns(2)
    with c1:
        st.session_state.user_data['banheiros'] = item_row("🛁 Banheiros", "q_ban")
        st.session_state.user_data['quartos'] = item_row("🛏️ Quartos", "q_quar")
        st.session_state.user_data['geladeiras'] = item_row("❄️ Geladeiras", "q_gel")
        # Campo Novo: Carro
        st.session_state.user_data['carros'] = item_row("🚗 Carro", "q_carro")
        
    with c2:
        st.session_state.user_data['tv_cores'] = item_row("📺 TV em Cores", "q_tv")
        st.session_state.user_data['computadores'] = item_row("💻 Computadores", "q_pc")
        st.session_state.user_data['celulares'] = item_row("📱 Celulares", "q_cel")
        # Campo Novo: Moto
        st.session_state.user_data['motos'] = item_row("🏍️ Moto", "q_moto")
        
    st.markdown("---")
    st.write("**Na sua casa tem**")
    c1, c2, c3 = st.columns(3)
    with c1: st.session_state.user_data['net'] = st.checkbox("🌐 Internet")
    with c3: st.session_state.user_data['tv_assinatura'] = st.checkbox("📡 TV por Assinatura e/ou streaming")

    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1: st.button("⬅️ Voltar", on_click=prev_step)
    with col_nav2: st.button("🚀 ENVIAR DADOS", type="primary", on_click=next_step)

# --- 3. CAMADA DE SERVIÇO (MOCK API & MAPPER) ---

def map_user_data_to_schema(ud):
    """
    Função pura que transforma os dados amigáveis da UI no JSON PLANO solicitado (De-Para).
    """
    letters = string.ascii_uppercase # A, B, C...

    def get_letter_code(val, source_list):
        if not val: return "A" # Fallback
        try:
            # Tenta encontrar o indice na lista (ignora "Selecione..." se for o caso)
            idx = source_list.index(val)
            return letters[idx] if idx < len(letters) else "A"
        except: return "A"

    def clean_qtd(val):
        if val == "Não tem": return 0
        if val == "4+": return 4
        return int(val)

    # Recriar lista de ocupação para garantir o índice correto (A, B, C...)
    ocups_list = [
        "Grupo 1 (Lavradores, agricultores sem empregados...)", 
        "Grupo 2 (Diaristas, domésticos, cuidadores...)", 
        "Grupo 3 (Profissionais de produção, metalúrgicos...)", 
        "Grupo 4 (Professores, técnicos, gerentes...)", 
        "Grupo 5 (Médicos, engenheiros, dentistas...)", 
        "Não sei"
    ]

    # Construção do Payload conforme solicitado (Flat JSON)
    payload = {
        # Identificação
        "id_ra_aluno": ud.get('ra_aluno'),
        "tp_faixa_etaria": MAPS['faixa_etaria'].get(ud.get('idade'), 0),
        "tp_sexo": "M" if ud.get('sexo') == "Masculino" else "F",
        "tp_nacionalidade": MAPS['nacionalidade'].get(ud.get('nacionalidade'), 0),
        "tp_cor_raca": MAPS['raca'].get(ud.get('cor_raca'), 0),
        "tp_estado_civil": MAPS['estado_civil'].get(ud.get('estado_civil'), 0),
        "q005": ud.get('pessoas_casa', 1),
        
        # Escolaridade
        "tp_st_conclusao": MAPS['situacao_em'].get(ud.get('situacao_em'), 0),
        "tp_ano_concluiu": 0 if ud.get('ano_conclusao') in ["Não informado", None] else (int(ud.get('ano_conclusao')) if ud.get('ano_conclusao').isdigit() else 0),
        "tp_escola": 2 if ud.get('tipo_escola') == "Pública" else (3 if ud.get('tipo_escola') == "Particular" else 0),
        "co_uf_esc": ud.get('uf_escola'),
        "no_municipio_esc": ud.get('municipio'),
        "tp_dependencia_adm_esc": MAPS['dependencia_adm'].get(ud.get('dependencia_adm'), 0),
        "tp_localizacao_esc": 1 if ud.get('localizacao_esc') == "Urbana" else 2,
        "in_certificado": 1 if ud.get('certificacao') else 0,
        
        # Socioeconômico
        "q001": get_letter_code(ud.get('pai_estudo'), MAPS['escolaridade']),
        "q002": get_letter_code(ud.get('mae_estudo'), MAPS['escolaridade']),
        "q003": get_letter_code(ud.get('pai_ocupacao'), ocups_list),
        "q004": get_letter_code(ud.get('mae_ocupacao'), ocups_list),
        "q006": get_letter_code(ud.get('renda'), MAPS['renda']),
        
        # Infraestrutura
        "q008": clean_qtd(ud.get('banheiros')),
        "q009": clean_qtd(ud.get('quartos')),
        "q010": clean_qtd(ud.get('carros')), # Novo (Carro)
        "q011": clean_qtd(ud.get('motos')),  # Novo (Moto)
        "q012": clean_qtd(ud.get('geladeiras')),
        "q019": clean_qtd(ud.get('tv_cores')),       # Mapeado para q019
        "q024": clean_qtd(ud.get('computadores')),
        "q022": clean_qtd(ud.get('celulares')),
        "q025": 1 if ud.get('net') else 0,
        "q020": 1 if ud.get('tv_assinatura') else 0  # Mapeado para q020
    }
    return payload

# Conexão com a AWS
def send_to_pipeline(payload):
    """
    Envia o JSON para a nuvem AWS via API Gateway.
    """
    API_URL = "https://h2ysd0xy7l.execute-api.sa-east-1.amazonaws.com/prod/submit" 

    headers = {"Content-Type": "application/json"}

    with st.spinner('Conectando ao Pipeline de Dados na AWS...'):
        try:
            # Para testes locais sem envio real, descomentar a linha abaixo:
            # return {"status": "success", "id": "TEST-123"}
            
            response = requests.post(API_URL, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success", 
                    "server_message": "Dados recebidos na nuvem.",
                    "id_transacao": data.get('id', 'N/A')
                }
            else:
                return {
                    "status": "error", 
                    "code": response.status_code,
                    "message": f"Erro AWS: {response.text}"
                }
                
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "Falha na conexão. Verifique sua internet."}
        except Exception as e:
            return {"status": "error", "message":str(e)}

# --- 4. TELA FINAL (Step 5) ---

def show_results():
    final_payload = map_user_data_to_schema(st.session_state.user_data)
    api_response = send_to_pipeline(final_payload)
    
    st.balloons()
    st.success("Muito obrigada pelas informações! Agora é com a gente!!")
    
    st.subheader("📦 JSON Enviado ao Pipeline")
    st.json(final_payload)
    
    st.subheader("📩 Resposta da API")
    st.json(api_response)

    if st.button("Responder novamente"):
        st.session_state.step = 1
        st.session_state.user_data = {}
        st.rerun()

# --- ROTEAMENTO ---
render_header()
if st.session_state.step == 1: step_1_identity()
elif st.session_state.step == 2: step_2_school()
elif st.session_state.step == 3: step_3_family()
elif st.session_state.step == 4: step_4_infrastructure()
elif st.session_state.step == 5: show_results()