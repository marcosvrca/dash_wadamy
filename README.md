# Wadamy — Inventário de Máquinas

Agente multiplataforma que coleta dados do PC e envia para um dashboard web centralizado.

## Estrutura

```
wadamy/
├── inventario.py              # Agente (Windows / Linux / macOS)
├── dashboard/
│   ├── app.py                 # API + dashboard Flask
│   └── templates/index.html
├── .github/workflows/
│   ├── build-windows.yml      # Gera inventario.exe
│   ├── build-linux.yml        # Gera binário Linux
│   └── dashboard.yml          # Testes do dashboard
└── render.yaml                # Deploy do dashboard no Render
```

## Dashboard local

**Windows (recomendado):** duplo clique em `iniciar-dashboard.bat`

Guia completo para o operador: [GUIA-COLEGA.md](GUIA-COLEGA.md)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python dashboard/app.py
```

Acesse: http://localhost:5000

## Agente local

```bash
pip install -r requirements-agent.txt

# Enviar para o dashboard local
export INVENTARIO_API_URL=http://localhost:5000/api/inventario
python inventario.py
```

Variáveis de ambiente do agente:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `INVENTARIO_API_URL` | `http://localhost:5000/api/inventario` | URL do endpoint POST |
| `INVENTARIO_HTML` | `1` | `1` gera e abre HTML local; `0` desativa |

## Subir para o GitHub

```bash
git init
git add .
git commit -m "Inventário multiplataforma com dashboard e CI"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/wadamy.git
git push -u origin main
```

## Baixar o .exe (sem Wine, sem VM)

1. Faça push do código para o GitHub
2. Vá em **Actions** → **Build Windows EXE**
3. Abra a execução mais recente
4. Baixe o artefato **inventario-windows**

O binário Linux fica em **Build Linux Binary** → artefato **inventario-linux**.

## Deploy do dashboard (Render — gratuito)

1. Crie conta em https://render.com
2. **New** → **Blueprint** → conecte o repositório GitHub
3. O Render lê o `render.yaml` e sobe o dashboard automaticamente
4. Anote a URL gerada (ex: `https://wadamy-dashboard.onrender.com`)

Configure o agente Windows:

```bat
set INVENTARIO_API_URL=https://wadamy-dashboard.onrender.com/api/inventario
inventario.exe
```

Para agendar no Windows (Task Scheduler), use essas variáveis de ambiente na tarefa.

## API

### `POST /api/inventario`

```json
{
  "hostname": "pc-01",
  "sistema": "Windows 10",
  "cpu": "Intel Core i5",
  "ram_gb": 16,
  "ram_livre": 8.5,
  "disco_gb": 512,
  "disco_livre": 200,
  "ip": "192.168.1.10",
  "cores": 8
}
```

### `GET /api/maquinas`

Retorna a última leitura de cada hostname.

### `GET /health`

Health check para monitoramento.
