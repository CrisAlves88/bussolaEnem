import streamlit as st
import json
import time
import requests

# Configuração da Págaina
st.set_page_config(page_title="Enem Compass - MVP", layout="centered")

# --- 1. CONFIGURAÇÃO E DICIONÁRIOS DE DADOS (MOCK DO INEP) ---

def get_inep_mappings():
    return {
        "raca": {"Selecione...":1,"Branca": 2, "Preta": 3, "Parda": 4, "Amarela": 5, "Indígena": 5, "Não declarado": 0},
        "escolaridade": [
            "Nunca estudou", "Não completou a 4ª série/5º ano do Ensino Fundamental.", 
            "Completou a 4ª série/5º ano, mas não completou a 8ª série/9º ano do Ensino Fundamental.",
            "Completou a 8ª série/9º ano do Ensino Fundamental, mas não completou o Ensino Médio.", 
            "Completou o Ensino Médio, mas não completou a Faculdade.", "Completou a Faculdade, mas não completou a Pós-graduação.", 
            "Completou a Pós-graduação.", "Não sei."
        ],
        "renda": [
            "Nenhuma renda.",
            "Até R$ 788,00.",
            "De R$ 788,01 até R$ 1.182,00.",
            "De R$ 1.182,01 até R$ 1.572,00.",
            "De R$ 1.572,01 até R$ 1.970,00.",
            "De R$ 1.970,01 até R$ 2.364,00.",
            "De R$ 2.364,01 até R$ 3.152,00.",
            "De R$ 3.152,01 até R$ 3.940,00.",
            "De R$ 3.940,01 até R$ 4.728,00.",
            "De R$ 4.728,01 até R$ 5.516,00.",
            "De R$ 5.516,01 até R$ 6.304,00.",
            "De R$ 6.304,01 até R$ 7.092,00.",
            "De R$ 7.092,01 até R$ 7.880,00.",
            "De R$ 7.880,01 até R$ 9.456,00.",
            "De R$ 9.456,01 até R$ 11.820,00.",
            "De R$ 11.820,01 até R$ 15.760,00.",
            "Mais de 15.760,00."
        ]       
    }

MAPS = get_inep_mappings()

if 'step' not in st.session_state:
    st.session_state.step = 1
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

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
    st.header("1. Queremos te conhecer! Por favor, preencha a tela abaixo")
    #______________
    # No código do ALUNO (step_1_identity), adicione isso:

def step_1_identity():
    st.header("1. Queremos te conhecer! Por favor, preencha a tela abaixo")
  
    st.info("Seu professor passou um código de turma, digite no campo abaixo.")
    st.session_state.user_data['turma_code'] = st.text_input("Código da Turma (Ex: ABC-12)", placeholder="").upper()
    
    st.markdown("---")
    # ... (Restante dos campos de idade, sexo, etc...)

    #_______________
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.user_data['idade'] = st.selectbox("Faixa Etária", ["Selecione...","Menor de 17 anos", "17 anos", "18 anos", "19 anos", 
                                                                            "20 anos","21 anos","22 anos","23 anos","24 anos","25 anos","entre 26 e 30 anos",
                                                                            "entre 31 e 35","entre 36 e 40 anos","entre 41 e 45 anos","entre 46 e 50 anos",
                                                                            "entre 51 e 55 anos","entre 56 e 60 anos","entre 61 e 65 anos","entre 66 e 70","Acima de 70 anos"])
        st.session_state.user_data['sexo'] = st.radio("Sexo", ["Masculino", 
                                                               "Feminino"], horizontal=True)
        st.session_state.user_data['nacionalidade'] = st.selectbox("Nacionalidade", ["Selecione...","Não informado", 
                                                                                     "Brasileiro(a)", 
                                                                                     "Brasileiro(a) Naturalizado(a)",
                                                                                     "Estrangeiro(a)",
                                                                                     "Brasileiro(a) Nato(a), nascido(a) no exterior"])
    with c2:
        st.session_state.user_data['cor_raca'] = st.selectbox("Cor/Raça", list(MAPS['raca'].keys()))
        st.session_state.user_data['estado_civil'] = st.selectbox("Estado Civil", ["Selecione...",
                                                                                   "Soleitro(a)", 
                                                                                   "Casado(a)/Mora com um(a) companheiro(a)",
                                                                                    "Divorciado(a)/Desquitado(a)/Separado(a)", 
                                                                                    "Viúvo(a)"])
        st.session_state.user_data['pessoas_casa'] = st.number_input("Pessoas na casa (incluindo você):", min_value=0, step=1)
    st.button("Próximo ➡️", on_click=next_step)

def step_2_school():
    st.header("2. Preencha sobre sua Escola")
    st.session_state.user_data['situacao_em'] = st.radio("Situação do Ensino Médio", 
                                                         ["Já concluí", "Estou cursando o último ano", 
                                                          "Estou cursando (não concluo este ano)"])
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.user_data['ano_conclusao'] = st.selectbox("Ano de Conclusão", ["Não informado",
                                                                                        "2015", 
                                                                                        "2014", "2013", 
                                                                                        "2012","2011", 
                                                                                        "2010", "2009",
                                                                                        "2008", "2007", 
                                                                                        "Anterior a 2007",])
        st.session_state.user_data['tipo_escola'] = st.selectbox("Tipo de Escola", ["Selecione...", 
                                                                                    "Pública",
                                                                                    "Particular"])
    with c2:
        st.session_state.user_data['uf_escola'] = st.selectbox("Estado (UF)", ["Selecione...","AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
                                                                                "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", 
                                                                                "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]) 
        st.session_state.user_data['municipio'] = st.text_input("Município", placeholder="Ex: São Paulo")
    st.markdown("##### Detalhes da Instituição")
    st.session_state.user_data['dependencia_adm'] = st.selectbox("Dependência Adm.", ["Selecione...","Estadual", "Municipal", "Federal", "Privada"])
    st.session_state.user_data['localizacao_esc'] = st.radio("Localização", ["Urbana", "Rural"], horizontal=True)
    st.session_state.user_data['certificacao'] = st.checkbox("Solicitei certificação do Ensino Médio pelo Enem?")
    
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1: st.button("⬅️ Voltar", on_click=prev_step)
    with col_nav2: st.button("Próximo ➡️", on_click=next_step)

def step_3_family():
    st.header("3. Contexto Familiar - nos conte um pouco sobre sua família")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.user_data['pai_estudo'] = st.selectbox("Meu pai estudou até:", MAPS['escolaridade'])
        st.session_state.user_data['mae_estudo'] = st.selectbox("Minha mãe estudou até:", MAPS['escolaridade'])
    with c2:
        ocups = ["Grupo 1 (Lavradores, agricultores sem empregados, bóias-frias e profissionais ligados à criação de animais, pesca, apicultura, extração vegetal e atividades rurais em geral.)", 
                 "Grupo 2 (Diaristas, domésticos, cuidadores, cozinheiros domésticos, motoristas particulares, faxineiros, vigilantes, porteiros, atendentes, auxiliares administrativos, vendedores, serventes e repositor.)", 
                 "Grupo 3 (Profissionais de produção e manutenção: padeiros, cozinheiros industriais, costureiros, sapateiros, metalúrgicos, operadores de máquinas, operários de fábrica, mineradores, pedreiros, pintores, eletricistas, encanadores, motoristas e taxistas.)", 
                 "Grupo 4 (Professores (não universitários), técnicos, policiais, militares de baixa patente, supervisores, gerentes, microempresários, pequenos comerciantes, pequenos proprietários rurais e trabalhadores autônomos.)", 
                 "Grupo 5 (Médicos, engenheiros, dentistas, psicólogos, advogados, juízes, delegados, oficiais de alta patente, professores universitários, diretores e donos de empresas médias/grandes.)", 
                 "Não sei"]
        st.session_state.user_data['pai_ocupacao'] = st.selectbox("Ocupação Pai", ocups)
        st.session_state.user_data['mae_ocupacao'] = st.selectbox("Ocupação Mãe", ocups)
    st.markdown("---")
    st.markdown("**Renda Mensal Familiar**")
    st.session_state.user_data['renda'] = st.selectbox("Selecione a faixa de renda total:", options=MAPS['renda'], index=None, placeholder="Selecione a faixa...")
    
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1: st.button("⬅️ Voltar", on_click=prev_step)
    with col_nav2: st.button("Próximo ➡️", on_click=next_step)

def step_4_infrastructure():
    st.header("4. Nos fale sobre sua casa")
    def item_row(label, key):
        c1, c2 = st.columns([3, 1])
        with c1: st.write(label)
        with c2: return st.selectbox(label, ["Não tem"]+[str(i) for i in range(1,4)]+["4+"], key=key, label_visibility="collapsed")

    c1, c2 = st.columns(2)
    with c1:
        st.session_state.user_data['banheiros'] = item_row("🛁 Banheiros", "q_ban")
        st.session_state.user_data['quartos'] = item_row("🛏️ Quartos", "q_quar")
        st.session_state.user_data['geladeiras'] = item_row("❄️ Geladeiras", "q_gel")
    with c2:
        st.session_state.user_data['tv_cores'] = item_row("📺 TV em Cores", "q_tv")
        st.session_state.user_data['computadores'] = item_row("💻 Computadores", "q_pc")
        st.session_state.user_data['celulares'] = item_row("📱 Celulares", "q_cel")
        
    st.markdown("---")
    st.write("**Na sua casa tem**")
    c1, c2, c3 = st.columns(3)
    with c1: st.session_state.user_data['net'] = st.checkbox("🌐 Internet")
    with c3: st.session_state.user_data['tv_assinatura'] = st.checkbox("📡 TV por Assinatura e/ou serviço de streaming")

    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1: st.button("⬅️ Voltar", on_click=prev_step)
    with col_nav2: st.button("🚀 ENVIAR DADOS", type="primary", on_click=next_step)

# --- 3. CAMADA DE SERVIÇO (MOCK API & MAPPER) ---

def map_user_data_to_schema(user_data):
    """
    Função pura que transforma os dados amigáveis da UI em códigos do Data Lake.
    """
    
    # Helpers de tradução
    def clean_qtd(val):
        if val == "Não tem": return 0
        if val == "4+": return 4
        return int(val)

    def get_renda_code(val):
        if not val: return "A" # Fallback
        idx = MAPS['renda'].index(val)
        import string
        letters = string.ascii_uppercase 
        return letters[idx] if idx < len(letters) else "Q"

    # Construção do Payload
    payload = {
        "student_profile": {
            "metadata": {
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": "mvp_web_onboarding"
            },
            "demographics": {
                "TP_SEXO": "M" if user_data.get('sexo') == "Masculino" else "F",
                "TP_COR_RACA": MAPS['raca'].get(user_data.get('cor_raca'), 0),
                "TP_ESTADO_CIVIL": 1,
                "Q005": user_data.get('pessoas_casa', 1)
            },
            "education_context": {
                "TP_ESCOLA": 2 if user_data.get('tipo_escola') == "Pública" else 3,
                "CO_UF_ESC": user_data.get('uf_escola', "SP"), 
                "NO_MUNICIPIO": user_data.get('municipio'),
                "IN_CERTIFICADO": 1 if user_data.get('certificacao') else 0
            },
            "socioeconomic_questions": {
                "Q001_PAI": "E", 
                "Q002_MAE": "E", 
                "Q006_RENDA": get_renda_code(user_data.get('renda')),
                "infrastructure": {
                    # --- ITENS EXISTENTES ---
                    "Q008_BANHEIRO": clean_qtd(user_data.get('banheiros')),
                    "Q009_QUARTOS": clean_qtd(user_data.get('quartos')),
                    "Q012_GELADEIRA": clean_qtd(user_data.get('geladeiras')),
                    "Q024_COMPUTADOR": clean_qtd(user_data.get('computadores')),
                    "Q025_INTERNET": 1 if user_data.get('net') else 0,
                    "Q014_TV_CORES": clean_qtd(user_data.get('tv_cores')),
                    #"Q013_DVD": clean_qtd(user_data.get('dvd')),
                    "Q022_CELULAR": clean_qtd(user_data.get('celulares')),
                    "Q019_TV_ASSINATURA": 1 if user_data.get('tv_assinatura') else 0
                }
            }
        }
    }
    return payload

#def send_to_pipeline(payload):
#  with st.spinner('Enviando para o Pipeline de Dados...'):
#        time.sleep(1.5) 
#        return {"status": "success", "cluster_id": "CLS_204", "message": "Dados recebidos e processados."}


#conexao com a AWS
def send_to_pipeline(payload):
    """
    Envia o JSON para a nuvem AWS via API Gateway.
    """
    
    # ---------------------------------------------------------
    # CONFIGURAÇÃO DA CONEXÃO
    # Cole aqui a URL que você gerou no passo anterior (API Gateway)
    # Exemplo: "https://a1b2c3d4.execute-api.us-east-1.amazonaws.com/prod/submit"
    API_URL = "https://h2ysd0xy7l.execute-api.sa-east-1.amazonaws.com/prod/submit" 
    # ---------------------------------------------------------

    headers = {"Content-Type": "application/json"}

    with st.spinner('Conectando ao Pipeline de Dados na AWS...'):
        try:
            # Envio real via POST
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
            return {
                        "status": "error", "message":str(e)
                    }
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