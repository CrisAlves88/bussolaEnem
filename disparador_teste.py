import json
import requests
import time

# --- CONFIGURAÇÃO ---
API_URL = "https://h2ysd0xy7l.execute-api.sa-east-1.amazonaws.com/prod/submit"
ARQUIVO_MASSA = "massa_teste_alunos.json"

def enviar_massa():
    # 1. Carrega os dados gerados
    with open(ARQUIVO_MASSA, "r", encoding="utf-8") as f:
        alunos = json.load(f)
    
    print(f"🚀 Iniciando envio de {len(alunos)} alunos para a AWS...")
    
    sucessos = 0
    erros = 0
    
    for i, payload in enumerate(alunos):
        try:
            # Envia para a API
            response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
            
            if response.status_code == 200:
                print(f"[{i+1}] ✅ Sucesso - RA: {payload['id_ra_aluno']}")
                sucessos += 1
            else:
                print(f"[{i+1}] ❌ Erro {response.status_code}: {response.text}")
                erros += 1
                
        except Exception as e:
            print(f"[{i+1}] ❌ Erro de Conexão: {str(e)}")
            erros += 1
            
        # Pequena pausa para não bloquear seu IP (opcional)
        time.sleep(0.1) 

    print("--- FIM DO TESTE DE CARGA ---")
    print(f"Total Enviado: {len(alunos)}")
    print(f"Sucessos: {sucessos}")
    print(f"Falhas: {erros}")

if __name__ == "__main__":
    enviar_massa()