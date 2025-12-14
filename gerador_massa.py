import json
import random
import uuid

# --- 1. BASE DE DADOS GEOGRÁFICA (UF -> MUNICÍPIOS REAIS) ---
# Agora com 10 Estados cobrindo todas as regiões do Brasil.

GEO_DATA = {
    # --- SUDESTE ---
    "SP": [
        "São Paulo", "Guarulhos", "Campinas", "São Bernardo do Campo", "Santo André",
        "Osasco", "Sorocaba", "Ribeirão Preto", "São José dos Campos", "Santos",
        "Mogi das Cruzes", "Diadema", "Jundiaí", "Piracicaba", "Carapicuíba",
        "Bauru", "Itaquaquecetuba", "São Vicente", "Franca", "Praia Grande",
        "Guarujá", "Taubaté", "Limeira", "Suzano", "Taboão da Serra",
        "Sumaré", "Barueri", "Embu das Artes", "São Carlos", "Indaiatuba"
    ],
    "RJ": [
        "Rio de Janeiro", "São Gonçalo", "Duque de Caxias", "Nova Iguaçu", "Niterói",
        "Belford Roxo", "Campos dos Goytacazes", "São João de Meriti", "Petrópolis", "Volta Redonda",
        "Magé", "Macaé", "Itaboraí", "Cabo Frio", "Angra dos Reis",
        "Nova Friburgo", "Barra Mansa", "Teresópolis", "Mesquita", "Nilópolis",
        "Maricá", "Rio das Ostras", "Queimados", "Resende", "Araruama",
        "Itaguaí", "Japeri", "São Pedro da Aldeia", "Itaperuna", "Barra do Piraí"
    ],
    "MG": [
        "Belo Horizonte", "Uberlândia", "Contagem", "Juiz de Fora", "Betim",
        "Montes Claros", "Ribeirão das Neves", "Uberaba", "Governador Valadares", "Ipatinga",
        "Sete Lagoas", "Divinópolis", "Santa Luzia", "Ibirité", "Poços de Caldas",
        "Patos de Minas", "Pouso Alegre", "Teófilo Otoni", "Barbacena", "Sabará",
        "Varginha", "Conselheiro Lafaiete", "Vespasiano", "Itabira", "Araguari",
        "Passos", "Ubá", "Coronel Fabriciano", "Muriaé", "Ituiutaba"
    ],

    # --- NORDESTE ---
    "BA": [
        "Salvador", "Feira de Santana", "Vitória da Conquista", "Camaçari", "Juazeiro",
        "Itabuna", "Lauro de Freitas", "Ilhéus", "Jequié", "Teixeira de Freitas",
        "Barreiras", "Alagoinhas", "Porto Seguro", "Simões Filho", "Paulo Afonso",
        "Eunápolis", "Santo Antônio de Jesus", "Valença", "Candeias", "Guanambi",
        "Jacobina", "Serrinha", "Senhor do Bonfim", "Dias d'Ávila", "Luís Eduardo Magalhães",
        "Itapetinga", "Irecê", "Campo Formoso", "Casa Nova", "Brumado"
    ],
    "PE": [
        "Recife", "Jaboatão dos Guararapes", "Olinda", "Caruaru", "Petrolina",
        "Paulista", "Cabo de Santo Agostinho", "Camaragibe", "Garanhuns", "Vitória de Santo Antão",
        "Igarassu", "São Lourenço da Mata", "Santa Cruz do Capibaribe", "Abreu e Lima", "Ipojuca",
        "Serra Talhada", "Araripina", "Gravatá", "Carpina", "Goiana",
        "Belo Jardim", "Arcoverde", "Ouricuri", "Escada", "Pesqueira",
        "Surubim", "Palmares", "Bezerros", "Moreno", "São Bento do Una"
    ],
    "CE": [
        "Fortaleza", "Caucaia", "Juazeiro do Norte", "Maracanaú", "Sobral",
        "Crato", "Itapipoca", "Maranguape", "Iguatu", "Quixadá",
        "Pacatuba", "Aquiraz", "Quixeramobim", "Canindé", "Russas",
        "Crateús", "Tianguá", "Aracati", "Cascavel", "Pacajus",
        "Icó", "Horizonte", "Camocim", "Morada Nova", "Acaraú",
        "Viçosa do Ceará", "Barbalha", "Limoeiro do Norte", "Tauá", "Trairi"
    ],

    # --- SUL ---
    "RS": [
        "Porto Alegre", "Caxias do Sul", "Canoas", "Pelotas", "Santa Maria",
        "Gravataí", "Viamão", "Novo Hamburgo", "São Leopoldo", "Rio Grande",
        "Alvorada", "Passo Fundo", "Sapucaia do Sul", "Uruguaiana", "Santa Cruz do Sul",
        "Cachoeirinha", "Bagé", "Bento Gonçalves", "Erechim", "Guaíba",
        "Cachoeira do Sul", "Santana do Livramento", "Esteio", "Ijuí", "Alegrete",
        "Sapiranga", "Lajeado", "Farroupilha", "Vacaria", "Campo Bom"
    ],
    "PR": [
        "Curitiba", "Londrina", "Maringá", "Ponta Grossa", "Cascavel",
        "São José dos Pinhais", "Foz do Iguaçu", "Colombo", "Guarapuava", "Paranaguá",
        "Araucária", "Toledo", "Apucarana", "Pinhais", "Campo Largo",
        "Arapongas", "Almirante Tamandaré", "Piraquara", "Umuarama", "Cambé",
        "Fazenda Rio Grande", "Sarandi", "Campo Mourão", "Francisco Beltrão", "Paranavaí",
        "Pato Branco", "Cianorte", "Telêmaco Borba", "Castro", "Rolândia"
    ],

    # --- CENTRO-OESTE ---
    "GO": [
        "Goiânia", "Aparecida de Goiânia", "Anápolis", "Rio Verde", "Águas Lindas de Goiás",
        "Luziânia", "Valparaíso de Goiás", "Trindade", "Formosa", "Novo Gama",
        "Senador Canedo", "Catalão", "Itumbiara", "Jataí", "Planaltina",
        "Caldas Novas", "Santo Antônio do Descoberto", "Goianésia", "Cidade Ocidental", "Mineiros",
        "Cristalina", "Inhumas", "Jaraguá", "Quirinópolis", "Niquelândia",
        "Morrinhos", "Goianira", "Porangatu", "Uruaçu", "Santa Helena de Goiás"
    ],

    # --- NORTE ---
    "PA": [
        "Belém", "Ananindeua", "Santarém", "Marabá", "Parauapebas",
        "Castanhal", "Abaetetuba", "Cametá", "Marituba", "Bragança",
        "São Félix do Xingu", "Barcarena", "Altamira", "Tucuruí", "Paragominas",
        "Tailândia", "Breves", "Itaituba", "Redenção", "Moju",
        "Novo Repartimento", "Oriximiná", "Santana do Araguaia", "Santa Izabel do Pará", "Capanema",
        "Breu Branco", "Tomé-Açu", "Igarapé-Miri", "Viseu", "Dom Eliseu"
    ]
}

# --- 2. FUNÇÕES AUXILIARES ---

def gerar_letra_aleatoria(max_index):
    """Gera letras de A até a letra correspondente ao índice (ex: 4 -> A,B,C,D,E)"""
    import string
    letras = string.ascii_uppercase
    # Limita para não estourar o alfabeto
    limit = min(max_index, len(letras))
    return letras[random.randint(0, limit-1)]

def gerar_aluno_fake():
    # 1. Escolha Geográfica Consistente (Estado e Cidade sempre batem)
    uf_escolhida = random.choice(list(GEO_DATA.keys()))
    cidade_escolhida = random.choice(GEO_DATA[uf_escolhida])

    # 2. Construção do Objeto JSON
    aluno = {
        # Identificação
        "id_ra_aluno": f"RA{random.randint(100000, 999999)}",
        "tp_faixa_etaria": random.randint(1, 20),
        "tp_sexo": random.choice(["M", "F"]),
        "tp_nacionalidade": random.choice([1, 1, 1, 2, 4]), # Peso maior para Brasileiro(1)
        "tp_cor_raca": random.choice([0, 1, 2, 3, 4, 5]),
        "tp_estado_civil": random.choice([1, 1, 1, 2, 3, 4]), # Peso maior para Solteiro(1)
        "q005": random.randint(1, 7), # Pessoas na casa

        # Escolaridade
        "tp_st_conclusao": random.choice([1, 2, 3]),
        "tp_ano_concluiu": random.choice([0] + [2023, 2024, 2025, 2026]*4), 
        "tp_escola": random.choice([2, 3]), # 2=Publica, 3=Privada
        "co_uf_esc": uf_escolhida,
        "no_municipio_esc": cidade_escolhida,
        "tp_dependencia_adm_esc": random.choice([1, 2, 2, 2, 3, 3, 4]), # Ponderado
        "tp_localizacao_esc": random.choice([1, 1, 1, 2]), # Ponderado Urbano
        "in_certificado": random.choice([0, 1]),

        # Socioeconômico
        "q001": gerar_letra_aleatoria(8),
        "q002": gerar_letra_aleatoria(8),
        "q003": gerar_letra_aleatoria(6),
        "q004": gerar_letra_aleatoria(6),
        "q006": gerar_letra_aleatoria(17), # Renda A-Q

        # Infraestrutura
        "q008": random.randint(0, 4), # Banheiros
        "q009": random.randint(1, 4), # Quartos
        "q010": random.choice([0, 0, 1, 1, 2]), # Carros (ponderado)
        "q011": random.choice([0, 0, 0, 1, 2]), # Motos (ponderado)
        "q012": random.randint(0, 2), # Geladeiras
        "q019": random.randint(0, 3), # TV Cores
        "q024": random.randint(0, 2), # Computador
        "q022": random.randint(0, 4), # Celular
        
        # Booleanos
        "q025": random.choice([0, 1, 1]), # Internet
        "q020": random.choice([0, 1])     # TV Assinatura
    }
    
    return aluno

# --- 3. EXECUÇÃO DA GERAÇÃO ---

QTD_REGISTROS = 500 # Defina a quantidade aqui
lista_final = []

print(f"🔄 Gerando {QTD_REGISTROS} registros de teste (Diversificados em 10 Estados)...")

for _ in range(QTD_REGISTROS):
    lista_final.append(gerar_aluno_fake())

# --- 4. SALVAR ARQUIVO JSON ---

NOME_ARQUIVO = "massa_teste_alunos.json"

try:
    with open(NOME_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(lista_final, f, indent=4, ensure_ascii=False)
    print(f"✅ Sucesso! Arquivo '{NOME_ARQUIVO}' gerado com {len(lista_final)} alunos.")
    print(f"🌍 Estados cobertos: {', '.join(GEO_DATA.keys())}")
    
except Exception as e:
    print(f"❌ Erro ao salvar arquivo: {e}")