# 📅 Shift Scheduler — Gerador de Escalas de Plantão

Automatiza a criação de escalas de trabalho semanais com base na disponibilidade de cada membro, distribuindo-os de forma equilibrada e aplicando um rodízio circular entre os dias.

## ✨ Como funciona

1. Os membros preenchem um formulário no Google Sheets informando sua disponibilidade semanal
2. O script lê essas respostas e distribui cada pessoa num dia da semana
3. A escala final é escrita automaticamente numa planilha do Google Sheets
4. A cada semana, o rodízio avança cada pessoa para o próximo dia disponível

### Lógica de escalação

- **Primeira execução:** cada pessoa é alocada no dia com menos gente (balanceamento)
- **Semanas seguintes:** cada pessoa avança para o dia imediatamente seguinte ao que trabalhou, respeitando sua disponibilidade (rodízio circular)
- **Se não houver disponibilidade** no próximo dia, o algoritmo tenta os seguintes. Se não achar nenhum, repete o mesmo dia
- **Pessoas fixas** nunca entram no rodízio e permanecem sempre no mesmo dia

## 🗂️ Estrutura do projeto

```
sheet-generator/
├── main.py           # Script principal
├── credencial.json   # Credenciais Google (não versionado)
├── historico.json    # Histórico da semana anterior (não versionado)
└── .gitignore
```

## ⚙️ Configuração

### 1. Dependências

```bash
pip install pandas gspread gspread-dataframe google-auth
```

### 2. Credenciais do Google

- Acesse o [Google Cloud Console](https://console.cloud.google.com/)
- Crie um projeto e ative as APIs **Google Sheets** e **Google Drive**
- Crie uma conta de serviço e baixe o arquivo JSON
- Renomeie para `credencial.json` e coloque na pasta do projeto
- Compartilhe as planilhas com o e-mail da conta de serviço

### 3. Planilhas

No `main.py`, configure as URLs das suas planilhas:

```python
# Planilha de disponibilidade (respostas do formulário)
url = 'https://docs.google.com/spreadsheets/d/SEU_ID/export?format=csv'

# Planilha de saída (escala final)
sheet = client.open_by_key("SEU_ID").sheet1
```

### 4. Pessoas fixas

Edite as listas no início do `main.py` para fixar pessoas em dias específicos:

```python
seg = ['Bruno', 'Aninha']
ter = ['Luiz', 'Aninha']
qua = ['Miguel']
qui = ['Anna Carolina']
sex = ['Nathan']
```

## ▶️ Uso

```bash
python main.py
```

A planilha de escala será atualizada automaticamente e o histórico salvo em `historico.json`.

## 📌 Observações

- O arquivo `credencial.json` **não deve ser versionado** — adicione-o ao `.gitignore`
- O `historico.json` é gerado automaticamente na primeira execução
- A planilha de disponibilidade deve ter as colunas: `membros`, `segunda`, `terca`, `quarta`, `quinta`, `sexta`
