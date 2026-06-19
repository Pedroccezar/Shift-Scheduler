import pandas as pd
import json
import os
from gspread_dataframe import set_with_dataframe
import gspread
from google.oauth2.service_account import Credentials

# ── Configuração ──────────────────────────────────────────────────────────────

HISTORICO_PATH = "historico.json"
ORDEM_DIAS = ["seg", "ter", "qua", "qui", "sex"]

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "credencial.json",
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open_by_key("SUA_PLANILHA_KEY").sheet1

url = 'https://docs.google.com/spreadsheets/d/SUA_PLANILHA_DISPONIBILIDADE/export?format=csv'
planilha = pd.read_csv(url)

# ── Pessoas fixas (nunca entram no rodízio) ───────────────────────────────────

seg      = ['Bruno']
ter      = ['Luiz']
qua      = ['Miguel']
qui      = ['Anna Carolina']
sex      = ['Nathan']
plantao  = []  # controle de quem já foi escalado

FIXOS = {pessoa for lista in [seg, ter, qua, qui, sex] for pessoa in lista}

dias_map = {"seg": seg, "ter": ter, "qua": qua, "qui": qui, "sex": sex}

# ── Histórico da semana anterior ──────────────────────────────────────────────

if os.path.exists(HISTORICO_PATH):
    with open(HISTORICO_PATH, "r", encoding="utf-8") as f:
        historico = json.load(f)
    print("Histórico carregado — rodízio ativado.")
else:
    historico = {}
    print("Nenhum histórico encontrado — primeira execução.")

# ── Função de rodízio ─────────────────────────────────────────────────────────

def proximo_dia_disponivel(dia_anterior, disponibilidade):
    """
    A partir do dia seguinte ao que a pessoa trabalhou,
    percorre os dias em ordem circular até achar um disponível.
    Se não achar nenhum, retorna o mesmo dia anterior.
    """
    idx_inicio = (ORDEM_DIAS.index(dia_anterior) + 1) % len(ORDEM_DIAS)

    for i in range(len(ORDEM_DIAS)):
        idx = (idx_inicio + i) % len(ORDEM_DIAS)
        dia = ORDEM_DIAS[idx]
        if disponibilidade.get(dia, False):
            return dia

    return dia_anterior  # nenhum dia disponível → repete o mesmo

# ── Escalação ─────────────────────────────────────────────────────────────────

novo_historico = {}

for i in planilha.itertuples():
    membro = i.membros.strip()  # remove espaços extras e problemas de encoding

    if membro in plantao or membro in FIXOS:
        continue

    disponibilidade = {
        "seg": bool(i.segunda),
        "ter": bool(i.terca),
        "qua": bool(i.quarta),
        "qui": bool(i.quinta),
        "sex": bool(i.sexta),
    }

    if membro in historico:
        # Rodízio: começa pelo dia seguinte ao da semana passada
        dia_escolhido = proximo_dia_disponivel(historico[membro], disponibilidade)
    else:
        # Primeira vez: escolhe o dia com menos pessoas
        dias_possiveis = [
            (dia, len(dias_map[dia]))
            for dia, disponivel in disponibilidade.items()
            if disponivel
        ]

        if not dias_possiveis:
            continue

        dia_escolhido = min(dias_possiveis, key=lambda x: x[1])[0]

    dias_map[dia_escolhido].append(membro)
    plantao.append(membro)
    novo_historico[membro] = dia_escolhido

# ── Salva histórico ───────────────────────────────────────────────────────────

with open(HISTORICO_PATH, "w", encoding="utf-8") as f:
    json.dump(novo_historico, f, ensure_ascii=False, indent=2)

print("Histórico salvo.")

# ── Exporta para o Google Sheets ──────────────────────────────────────────────

planilha_def = pd.DataFrame({
    'Segunda': pd.Series(seg),
    'Terça':   pd.Series(ter),
    'Quarta':  pd.Series(qua),
    'Quinta':  pd.Series(qui),
    'Sexta':   pd.Series(sex)
})

planilha_def = planilha_def.fillna('')
sheet.clear()
set_with_dataframe(sheet, planilha_def)
print("Planilha feita!")
