## Bússola do ENEM - MVP (Frontend & Ingestão)

Diagnóstico educacional personalizado baseado em Big Data do INEP.

O Bússola do ENEM é uma plataforma de inteligência de dados projetada para democratizar estratégias de estudo de alta performance. O sistema coleta dados socioeconômicos e educacionais do aluno, cruza com o histórico de microdados do ENEM (2015-2021) e identifica padrões (clusters) para sugerir planos de estudo focados nas lacunas reais de aprendizado.

Este repositório contém o Frontend da Aplicação (Streamlit) responsável pela jornada de onboarding do aluno e envio dos dados para o Pipeline na Nuvem (AWS).

## Arquitetura da Solução
O projeto segue uma arquitetura Serverless moderna focada em escalabilidade e baixo custo.

* Frontend (Este Repo):  Aplicação em Python/Streamlit que guia o aluno por um formulário wizard (4 etapas).

* API Gateway (AWS):Ponto de entrada seguro que recebe o payload JSON.

* Processamento (AWS Lambda): Função serverless que valida e ingere os dados.

* Data Lake (AWS S3): Armazenamento dos dados brutos na camada Bronze (Raw).

Snippet de código

*graph LR*
    A[Aluno/Streamlit] -->|JSON POST| B[AWS API Gateway]
    B -->|Proxy| C[AWS Lambda]
    C -->|Save .json| D[(AWS S3 - Bronze)]
    
## Funcionalidades do MVP
Jornada do Usuário Guiada (Wizard): Interface dividida em 4 passos lógicos para reduzir a fricção e o abandono (Identificação, Escola, Família, Infraestrutura).

* Mapeamento INEP: Conversão automática das respostas amigáveis para os códigos técnicos do dicionário de dados do INEP (ex: Renda, Escolaridade, Raça).

* Vínculo com Turmas: Campo para inserção de "Código da Turma", permitindo análises B2B2C (visão do Professor/Escola).

* Integração Cloud-Native: Envio direto dos dados para a AWS via API REST.

* Responsividade: Interface otimizada para Desktop e Mobile.

## Tecnologias Utilizadas
* Linguagem: Python 3.9+

* Framework Web: Streamlit

* Comunicação: Requests (HTTP Library)

* Cloud (Backend): AWS (API Gateway, Lambda, S3)

## Como Executar o Projeto Localmente
Pré-requisitos
* Python instalado.

* Conta na AWS (para configurar o backend, caso queira alterar o endpoint).

## Passo a Passo
Clone o repositório:

Bash

git clone https://github.com/seu-usuario/bussola-enem-mvp.git
cd bussola-enem-mvp
Crie um ambiente virtual (recomendado):

Bash

python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
Instale as dependências:

Bash

pip install streamlit requests
Execute a aplicação:

Bash

streamlit run app.py
Acesse no navegador: http://localhost:8501

## Estrutura de Dados (JSON Schema)
O Frontend envia os dados no seguinte formato para o Data Lake, garantindo compatibilidade com os processos de ETL futuros:

JSON

{
  "student_profile": {
    "metadata": {
      "created_at": "YYYY-MM-DD HH:MM:SS",
      "source": "mvp_web_onboarding"
    },
    "demographics": {
      "TP_SEXO": "M/F",
      "TP_COR_RACA": "Int (Código INEP)",
      "Q005": "Int (Pessoas na casa)"
    },
    "education_context": {
      "COD_TURMA": "String (Vínculo Escola)",
      "TP_ESCOLA": "Int",
      "CO_UF_ESC": "String (UF)"
    },
    "socioeconomic_questions": {
      "Q006_RENDA": "Char (A-Q)",
      "infrastructure": {
        "Q024_COMPUTADOR": "Int",
        "Q025_INTERNET": "0/1"
      }
    }
  }
}
## Configuração
No arquivo app.py, a URL do API Gateway está definida na função send_to_pipeline.

Python

# app.py
API_URL = "https://h2ysd0xy7l.execute-api.sa-east-1.amazonaws.com/prod/submit"
Nota: Em ambiente de produção, recomenda-se mover esta URL para variáveis de ambiente (st.secrets no Streamlit).

## Roadmap e Próximos Passos
[X] MVP 1.0: Coleta de dados e Ingestão no S3 (Bronze).

[X] MVP 1.0: Integração com simulado de questões.

[X] Backend: Crawler do AWS Glue para catalogar dados na camada Silver.

[X] Data Science: Modelo de Clustering para perfilamento do aluno.

[X] Frontend: Dashboard de Resultados (Aluno) e Portal do Educador.
