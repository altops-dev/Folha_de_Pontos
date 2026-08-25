# Folha de Pontos

Aplicação web em **Python (Flask)** para registrar entrada e saída de colaboradores pelo celular, na rede local da empresa. Os eventos são gravados numa **Google Sheet**. Cada pessoa autentica-se com nome e PIN e só consegue registrar o próprio ponto.

O computador da empresa hospeda a aplicação durante o expediente. Não é necessário um servidor dedicado, nem expor o sistema na internet.

Este repositório está preparado como **case de portfólio**: o código é público; credenciais, ID da planilha e dados reais ficam só na máquina que executa o sistema.

## Sumário

- [Funcionalidades](#funcionalidades)
- [Como funciona](#como-funciona)
- [Tecnologias](#tecnologias)
- [Arquitetura](#arquitetura)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Google Cloud e Google Sheets](#google-cloud-e-google-sheets)
- [Credenciais e variáveis de ambiente](#credenciais-e-variáveis-de-ambiente)
- [Usuários](#usuários)
- [Executar sem Docker](#executar-sem-docker)
- [Executar com Docker](#executar-com-docker)
- [Acesso pelos celulares](#acesso-pelos-celulares)
- [Planilha e cálculo de horas](#planilha-e-cálculo-de-horas)
- [Publicar no GitHub](#publicar-no-github)
- [CI](#ci)
- [Solução de problemas](#solução-de-problemas)
- [Limitações](#limitações)
- [Licença](#licença)

## Funcionalidades

- Login por nome (lista) e PIN individual
- Registro de **Entrada** e **Saída**
- Mensagem de confirmação ou erro após cada tentativa
- Persistência na primeira aba da planilha: colaborador, data, hora e tipo
- Execução local com Python ou em contêiner Docker
- Credenciais fora do Git (`service_account.json` e `.env`)

## Como funciona

O Flask escuta na rede local (`0.0.0.0`). Os celulares acessam o IP do computador, por exemplo `http://192.168.0.8:5000`.

Depois do login, a sessão guarda o nome autenticado. Ao carregar num botão, o servidor usa a data/hora do computador hospedeiro e envia a linha à planilha através da conta de serviço.

```text
Celular do colaborador
        │
        │  HTTP na rede local
        ▼
Computador da empresa (Flask)
        │
        │  Google Sheets API (conta de serviço)
        ▼
Planilha (aba REGISTROS)
```

Uso previsto: **rede local controlada**. Não publique esta aplicação diretamente na internet sem HTTPS, autenticação mais forte e um servidor WSGI.

## Tecnologias


| Camada       | Tecnologia           | Função                                            |
| ------------ | -------------------- | ------------------------------------------------- |
| Backend      | Python 3.11+         | Lógica da aplicação                               |
| Web          | Flask                | Rotas, sessões e formulários                      |
| Interface    | HTML, CSS, Jinja2    | Telas no celular                                  |
| Integração   | gspread, google-auth | Escrita na planilha                               |
| Configuração | python-dotenv        | Variáveis no arquivo `.env`                       |
| Contentores  | Docker Compose       | Ambiente reproduzível                             |
| CI           | GitHub Actions       | Ruff, Bandit, pip-audit e bloqueio de credenciais |


## Arquitetura


| Ficheiro               | Responsabilidade                            |
| ---------------------- | ------------------------------------------- |
| `app.py`               | Flask, login, sessão e rotas de registro    |
| `sheets_handler.py`    | Ligação à Sheets e `append_row`             |
| `templates/`           | Páginas Jinja2 (`login.html`, `index.html`) |
| `static/style.css`     | Estilos                                     |
| `.env`                 | Segredos e configuração **local**           |
| `service_account.json` | Chave da conta de serviço **local**         |


O ID da planilha e o caminho das credenciais vêm do ambiente (`SPREADSHEET_ID`, `GOOGLE_APPLICATION_CREDENTIALS`). Não devem estar hardcoded no código publicado.

## Estrutura do projeto

```text
Folha_de_Pontos_Local/
├── app.py
├── sheets_handler.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .env.example                  # público
├── .env                          # só local; não commitar
├── service_account.example.json  # público, valores fictícios
├── service_account.json          # só local; não commitar
├── .github/workflows/security.yml
├── templates/
│   ├── index.html
│   └── login.html
└── static/
    └── style.css
```

## Pré-requisitos

- Python 3.11 ou superior **ou** Docker Desktop (WSL 2 no Windows)
- Conta Google com acesso ao [Google Cloud Console](https://console.cloud.google.com/)
- Uma planilha no Google Sheets
- Computador hospedeiro ligado à rede da empresa
- Celulares na **mesma** rede Wi-Fi/LAN

## Google Cloud e Google Sheets

### 1. Projeto

Crie um projeto no Console (por exemplo `folha-de-pontos`). Confirme que está selecionado ao criar a conta de serviço.

### 2. APIs

Ative:

- **Google Sheets API**
- **Google Drive API** (o gspread pode precisar dela para abrir a planilha)

### 3. Conta de serviço

Em **APIs e serviços → Credenciais**, crie uma conta de serviço. Abra a conta, vá a **Chaves** e gere uma chave **JSON**.

Guarde o arquivo baixado na raiz do projeto com o nome:

```text
service_account.json
```

No Windows, evite a extensão duplicada `service_account.json.json` (explorador a ocultar extensões).

### 4. Compartilhar a planilha

Abra o JSON, copie `client_email` e compartilhe a planilha com esse endereço, permissão **Editor**.

### 5. ID da planilha

Na URL, o ID está entre `/d/` e `/edit`:

```text
https://docs.google.com/spreadsheets/d/ID_DA_PLANILHA/edit
```

Esse valor vai para `SPREADSHEET_ID` no `.env`, não para o código.

## Credenciais e variáveis de ambiente

```powershell
Copy-Item .env.example .env
Copy-Item service_account.example.json service_account.json
```

Substitua `service_account.json` pelo JSON real do Google. Preencha o `.env`:

```env
SPREADSHEET_ID=cole_o_id_da_planilha_aqui
GOOGLE_APPLICATION_CREDENTIALS=service_account.json
FLASK_SECRET_KEY=troque-por-uma-string-longa-aleatoria
FLASK_DEBUG=false
PORT=5000
USERS_JSON={"Ana":"1234","Bruno":"5678","Carla":"9012","Diego":"3456"}
```


| Variável                         | Função                                                                               |
| -------------------------------- | ------------------------------------------------------------------------------------ |
| `SPREADSHEET_ID`                 | Planilha de destino                                                                  |
| `GOOGLE_APPLICATION_CREDENTIALS` | Caminho do JSON da conta de serviço                                                  |
| `FLASK_SECRET_KEY`               | Assinatura da sessão (defina uma chave estável; senão a sessão muda a cada reinício) |
| `FLASK_DEBUG`                    | `true` só na sua máquina, em desenvolvimento                                         |
| `PORT`                           | Porta do Flask (padrão: 5000)                                                        |
| `USERS_JSON`                     | Mapa nome → PIN (JSON numa linha)                                                    |


Nunca commite `.env` nem `service_account.json`. O `.gitignore` já os exclui. A imagem Docker também não os copia: o Compose monta o JSON em runtime e injeta o `.env`.

## Usuários

Os nomes da lista de login vêm de `USERS_JSON`. Sem essa variável, a aplicação usa o conjunto de demonstração (Ana, Bruno, Carla, Diego).

Para o dia a dia da empresa, edite só o `.env` local. **Não** coloque nomes reais nem PINs reais num repositório público.

Num produto real, os PINs deveriam estar com hash numa base de dados. Aqui o dicionário é deliberadamente simples, para o case.

## Executar sem Docker

Na pasta do projeto (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Se o PowerShell bloquear scripts:

```cmd
.venv\Scripts\activate.bat
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

O servidor escuta em `0.0.0.0` para aceitar os celulares. No próprio computador: `http://127.0.0.1:5000`.

## Executar com Docker

Requisitos: Docker Desktop a correr; `.env` e `service_account.json` preenchidos.

```powershell
docker compose up -d --build
docker compose ps
docker compose logs -f
```

Parar:

```powershell
docker compose down
```

Mapeamento de portas no `docker-compose.yml`: `"5000:5000"` (externa:interna). Se a 5000 estiver ocupada no Windows, altere só o primeiro número, por exemplo `"5050:5000"`. Os celulares passam a usar a porta **5050**.

`restart: unless-stopped` relança o contêiner após falhas. No Docker Desktop, ative **Start Docker Desktop when you log in** se quiser que o sistema volte depois de reiniciar o PC.

A imagem copia apenas o código (`app.py`, `sheets_handler.py`, templates e static). O JSON **não** entra no build.

## Acesso pelos celulares

1. Computador e celular na mesma LAN.
2. No Windows: `ipconfig` → **Endereço IPv4** (ex.: `192.168.0.8`).
3. No celular: `http://192.168.0.8:5000` (ou a porta externa do Compose).

`localhost` no celular aponta para o próprio celular, não para o PC.

Para o IP não mudar, use reserva DHCP ou IP estático, conforme a política da empresa.

### Firewall

Se abrir no PC e não no celular, crie uma regra de **entrada** TCP na porta externa (5000 ou 5050) no perfil de **rede privada**. Não abra a porta em redes públicas sem necessidade.

## Planilha e cálculo de horas

Na primeira linha da aba de registros (a aplicação usa `sheet1`):


| Coluna | Cabeçalho   | Exemplo    |
| ------ | ----------- | ---------- |
| A      | Colaborador | Ana        |
| B      | Data        | 25/08/2026 |
| C      | Hora        | 08:00:00   |
| D      | Tipo        | Entrada    |


O código envia `[nome, data, hora, tipo]` com `append_row`. Os cabeçalhos não bloqueiam a escrita; a **ordem** das colunas precisa coincidir.

Boa prática: aba `REGISTROS` (dados brutos) e aba `RELATORIO` (uma linha por colaborador e data).

Com `A2` = nome, `B2` = data, e as colunas A–D em `REGISTROS` (separador `;` no Google Sheets em português):

Jornada do dia (soma das saídas menos soma das entradas):

```text
=SOMASES(REGISTROS!$C:$C;REGISTROS!$A:$A;$A2;REGISTROS!$B:$B;$B2;REGISTROS!$D:$D;"Saída")-SOMASES(REGISTROS!$C:$C;REGISTROS!$A:$A;$A2;REGISTROS!$B:$B;$B2;REGISTROS!$D:$D;"Entrada")
```

Saldo face a 8 horas:

```text
=(SOMASES(REGISTROS!$C:$C;REGISTROS!$A:$A;$A2;REGISTROS!$B:$B;$B2;REGISTROS!$D:$D;"Saída")-SOMASES(REGISTROS!$C:$C;REGISTROS!$A:$A;$A2;REGISTROS!$B:$B;$B2;REGISTROS!$D:$D;"Entrada"))-TEMPO(8;0;0)
```

Formate o resultado como **Duração**. Ajuste intervalos, folgas, feriados e registros incompletos antes de usar o relatório em produção. Falta não se infere só da ausência de linha: é preciso um calendário de dias esperados.

## Publicar no GitHub

### Pode ir para o repositório

Código, templates, CSS, `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `.env.example`, `service_account.example.json` (só valores fictícios), workflow de CI.

### Não pode ir


| Item                            | Motivo                                     |
| ------------------------------- | ------------------------------------------ |
| `service_account.json`          | `private_key` dá acesso à API e à planilha |
| `.env`                          | ID da planilha, secret do Flask, PINs      |
| PINs e nomes reais              | Impersonação e dados pessoais              |
| Backups/logs com horários reais | Informação laboral                         |


Antes do commit:

```bash
git add .
git status
```

Confirme que `service_account.json` e `.env` **não** aparecem. Depois:

```bash
git commit -m "Documenta e prepara a folha de pontos para um case público."
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```

Se o GitHub já tiver um commit inicial:

```bash
git pull --rebase origin main
git push -u origin main
```

### Se uma chave já foi publicada

Apagar o arquivo num commit novo **não é suficiente**: a chave fica no histórico. No Google Cloud, revogue a chave, gere outra e atualize o JSON local. Limpe o histórico (`git filter-repo` ou equivalente) e reveja forks, releases e caches. Se a planilha tiver dados reais, reveja compartilhamentos e o responsável pela proteção de dados.

## CI

O workflow `.github/workflows/security.yml` corre em `push`/`pull_request` para `main` e `master`:

- Falha se `service_account.json` ou `.env` estiverem no repositório
- Ruff (qualidade; não falha o job)
- Bandit (segurança estática)
- pip-audit (vulnerabilidades nas dependências)

## Solução de problemas

`**service_account.json` não encontrado**  
O arquivo precisa estar na raiz (ou no caminho de `GOOGLE_APPLICATION_CREDENTIALS`). No Docker, o volume deve montar `./service_account.json` em `/app/service_account.json`.

**403 / Drive API**  
Ative Sheets e Drive no **mesmo** projeto do `project_id` do JSON. Compartilhe a planilha com o `client_email` certo.

**YAML do Compose**  
Indentação com espaços, não tabs. Comando atual: `docker compose` (sem hífen).

**Celular não abre**  
`docker compose ps` ou o processo Python ativo; mesma rede; porta correta; firewall; teste primeiro `http://127.0.0.1:5000` no PC.

**Confirma na app e não aparece na folha**  
Logs (`docker compose logs -f` ou o terminal do Python), ID no `.env`, conta de serviço editor, primeira aba da planilha.

**Sessão cai sempre que reinicia**  
Defina `FLASK_SECRET_KEY` fixa no `.env`.

## Limitações

Versão para rede interna e estudo. Para produção mais exigente: base de dados, hash de PINs, CSRF, limite de tentativas de login, HTTPS, WSGI (gunicorn/waitress), auditoria, regras de jornada e conformidade com privacidade (incluindo LGPD, se aplicável).



## Autor

**Miguel Altino Silva** — case de automação, Flask, integração com Google Sheets e Docker.

## Referências

- [Python](https://docs.python.org/3/)
- [Flask](https://flask.palletsprojects.com/)
- [gspread](https://docs.gspread.org/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Docker Compose](https://docs.docker.com/compose/)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

