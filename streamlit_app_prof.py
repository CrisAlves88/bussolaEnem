import streamlit as st
import random
import string
import time

# Configuração da Página
st.set_page_config(page_title="Portal do Educador - Enem Compass", layout="wide", page_icon="🏫")

# --- MOCK DATABASE (Simulando o Backend) ---
if 'schools_db' not in st.session_state:
    st.session_state.schools_db = []
if 'generated_classes' not in st.session_state:
    st.session_state.generated_classes = []

# --- FUNÇÕES UTILITÁRIAS ---

def generate_class_code():
    """Gera um código único curto (ex: A7X-22) para o aluno digitar."""
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(chars) for _ in range(6))
    return f"{code[:3]}-{code[3:]}"

def save_school_data(data):
    """Simula o salvamento no Banco de Dados/S3"""
    time.sleep(1) # Fake loading
    st.session_state.schools_db.append(data)
    # Aqui entraria o código para salvar no AWS DynamoDB ou RDS
    return True

# --- INTERFACE DO USUÁRIO ---

def render_sidebar():
    with st.sidebar:
        st.header("🏫 Menu Professor")
        st.info("Bem-vindo ao Enem Compass for Schools.")
        st.markdown("---")
        st.markdown("""
        **Como funciona:**
        1. Cadastre sua escola.
        2. Crie uma turma.
        3. Compartilhe o **Código** com seus alunos.
        4. Receba o relatório consolidado.
        """)

def render_school_registration():
    st.title("🏫 Cadastro de Instituição e Turmas")
    st.write("Preencha os dados para habilitar o diagnóstico dos seus alunos.")

    with st.form("school_register_form"):
        st.subheader("1. Dados do Educador")
        c1, c2 = st.columns(2)
        with c1:
            teacher_name = st.text_input("Nome do Professor/Coordenador")
        with c2:
            teacher_email = st.text_input("Email Institucional")

        st.subheader("2. Dados da Escola")
        st.warning("💡 O Código INEP é essencial para cruzarmos os dados com o histórico oficial do governo.")
        
        c3, c4 = st.columns([1, 3])
        with c3:
            inep_code = st.text_input("Código INEP da Escola", max_chars=8, help="Código de 8 dígitos do censo escolar.")
        with c4:
            school_name = st.text_input("Nome da Escola")

        c5, c6, c7 = st.columns(3)
        with c5:
            uf = st.selectbox("Estado (UF)", ["SP", "RJ", "MG", "BA", "RS", "Outro"])
        with c6:
            city = st.text_input("Município")
        with c7:
            admin_dep = st.selectbox("Dependência Administrativa", ["Estadual", "Municipal", "Federal", "Privada"])

        st.subheader("3. Criação da Turma Inicial")
        class_name = st.text_input("Nome da Turma para Análise", placeholder="Ex: 3º Ano A - Matutino")

        # Botão de Submit
        submitted = st.form_submit_button("✅ Cadastrar e Gerar Código para Alunos", type="primary")

        if submitted:
            if not teacher_name or not school_name or not class_name:
                st.error("Por favor, preencha os campos obrigatórios.")
            else:
                # Lógica de Sucesso
                new_code = generate_class_code()
                
                school_payload = {
                    "teacher": teacher_name,
                    "email": teacher_email,
                    "inep": inep_code,
                    "school": school_name,
                    "uf": uf,
                    "city": city,
                    "type": admin_dep,
                    "class_name": class_name,
                    "class_code": new_code, # CHAVE DE VÍNCULO
                    "created_at": time.strftime("%Y-%m-%d")
                }
                
                save_school_data(school_payload)
                st.session_state.last_created_code = new_code
                st.session_state.last_created_class = class_name
                st.success("Escola e Turma cadastradas com sucesso!")

def render_dashboard_view():
    """Tela de Sucesso após cadastro"""
    if 'last_created_code' in st.session_state:
        st.markdown("---")
        st.header("🎉 Tudo pronto!")
        
        col_destaque, col_info = st.columns([2, 3])
        
        with col_destaque:
            st.info(f"""
            ### Código da Turma:
            # `{st.session_state.last_created_code}`
            """)
            st.caption("Peça para os alunos digitarem este código no início do questionário.")
        
        with col_info:
            st.subheader(f"Turma: {st.session_state.last_created_class}")
            st.write("🔗 **Link direto para alunos (Simulação):**")
            st.code(f"https://enem-compass.app/aluno?code={st.session_state.last_created_code}")
            
            st.markdown("#### 📊 O que acontece agora?")
            st.write("""
            1. O aluno preenche o diagnóstico.
            2. Nosso Pipeline processa as lacunas de aprendizado.
            3. O sistema cruza com o perfil socioeconômico.
            4. **Você recebe um PDF com:** "Alunos de baixa renda desta turma estão com dificuldade crítica em Geometria, desviando 30% da média de escolas semelhantes".
            """)

# --- RENDERIZAÇÃO PRINCIPAL ---
render_sidebar()
render_school_registration()
render_dashboard_view()