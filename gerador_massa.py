import json
import random
import time
import uuid

# --- CONFIGURAÇÕES ---
QTD_REGISTROS = 100
ARQUIVO_SAIDA = "massa_teste_enem.json"

# --- OPÇÕES POSSÍVEIS (DOMÍNIOS) ---
OPCOES = {
    "sexo": ["M", "F"],
    "cor_raca": [0, 1, 2, 3, 4, 5], # Baseado no seu MAPS
    "renda": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q"],
    "uf": ["SP", "RJ", "MG", "BA", "RS", "PE", "CE", "AM"],
    "municipios": ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Salvador", "Recife", "Manaus"],
    "escolaridade_pais": ["A", "B", "C", "D", "E", "F", "G"], # Mapeado para letras genéricas
}

def gerar_aluno_fake(index):
    """Gera um único objeto JSON de aluno com dados aleatórios"""
    
    # Gera um RA aleatório (Ex: 2024001)
    ra_fake = f"{2024000 + index}"
    
    return {
        "student_profile": {
            "metadata": {
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": "script_qa_mass_generation",
                "test_batch_id": "LOTE_001"
            },
            "demographics": {
                "ID_RA_ALUNO": ra_fake,
                "TP_SEXO": random.choice(OPCOES["sexo"]),
                "TP_COR_RACA": random.choice(OPCOES["cor_raca"]),
                "TP_ESTADO_CIVIL": random.randint(0, 4),
                "Q005": random.randint(1, 12) # Pessoas na casa
            },
            "education_context": {
                "TP_ESCOLA": random.choice([2, 3]), # 2=Pública, 3=Privada
                "CO_UF_ESC": random.choice(OPCOES["uf"]),
                "NO_MUNICIPIO": random.choice(OPCOES["municipios"]),
                "IN_CERTIFICADO": random.choice([0, 1])
            },
            "socioeconomic_questions": {
                "Q001_PAI": random.choice(OPCOES["escolaridade_pais"]),
                "Q002_MAE": random.choice(OPCOES["escolaridade_pais"]),
                "Q006_RENDA": random.choice(OPCOES["renda"]),
                "infrastructure": {
                    "Q008_BANHEIRO": random.randint(1, 4),
                    "Q009_QUARTOS": random.randint(1, 5),
                    "Q012_GELADEIRA": random.randint(1, 3),
                    "Q024_COMPUTADOR": random.randint(0, 3),
                    "Q025_INTERNET": random.choice([0, 1]),
                    "Q014_TV_CORES": random.randint(0, 4),
                    "Q022_CELULAR": random.randint(0, 5),
                    "Q019_TV_ASSINATURA": random.choice([0, 1])
                }
            }
        }
    }

# --- EXECUÇÃO ---
print(f"🔄 Gerando {QTD_REGISTROS} registros...")

lista_alunos = []
for i in range(QTD_REGISTROS):
    aluno = gerar_aluno_fake(i)
    lista_alunos.append(aluno)

# Salva em arquivo
with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
    json.dump(lista_alunos, f, indent=2, ensure_ascii=False)

print(f"✅ Sucesso! Arquivo '{ARQUIVO_SAIDA}' criado com 100 JSONs.")
print("Exemplo do primeiro registro:")
print(json.dumps(lista_alunos[0], indent=2, ensure_ascii=False))