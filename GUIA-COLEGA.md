# Guia rápido — Inventário Wadamy

Passo a passo para operar o sistema no seu PC.

---

## O que é isso?

Várias máquinas da rede enviam dados (hostname, CPU, RAM, disco, IP) automaticamente. **Só o seu PC** recebe e exibe tudo num dashboard no navegador.

```
[Outros PCs]  ──enviam dados──>  [Seu PC]  ──você vê──>  Dashboard no navegador
```

---

## Parte 1 — Preparar o seu PC (uma vez só)

### 1. Instalar o Python (se ainda não tiver)

1. Acesse: https://www.python.org/downloads/
2. Baixe e instale o Python 3
3. **Importante:** na instalação, marque **"Add Python to PATH"**

### 2. Baixar o projeto

Abra o **Prompt de Comando** ou **PowerShell** e rode:

```bat
git clone https://github.com/marcosvrca/dash_wadamy.git
cd dash_wadamy
```

> Se não tiver Git: baixe o ZIP em https://github.com/marcosvrca/dash_wadamy → **Code** → **Download ZIP**, extraia e entre na pasta.

### 3. Subir o dashboard

Dê **duplo clique** no arquivo:

```
iniciar-dashboard.bat
```

Na primeira vez ele instala tudo sozinho (pode demorar um pouco).

Quando aparecer algo assim, está funcionando:

```
Dashboard local:  http://localhost:5000
IP desta maquina: 192.168.x.x
URL para os agentes: http://192.168.x.x:5000/api/inventario
```

### 4. Abrir o dashboard

No navegador, acesse:

```
http://localhost:5000
```

**Anote o IP que apareceu** (ex: `192.168.1.50`) — você vai usar nas outras máquinas.

### 5. Manter rodando

**Deixe a janela preta aberta** enquanto quiser receber dados. Fechou a janela = dashboard parou.

---

## Parte 2 — Configurar as outras máquinas

### 1. Baixar o agente (`inventario.exe`)

1. Acesse: https://github.com/marcosvrca/dash_wadamy/actions
2. Clique em **Build Windows EXE** (execução mais recente com ✓ verde)
3. Role até **Artifacts** e baixe **inventario-windows**
4. Extraia o `inventario.exe` e copie para cada PC que será monitorado

### 2. Testar numa máquina

Abra o **Prompt de Comando** na pasta do `inventario.exe` e rode (troque o IP pelo **seu**):

```bat
set INVENTARIO_API_URL=http://192.168.1.50:5000/api/inventario
set INVENTARIO_HTML=0
inventario.exe
```

| Variável | O que faz |
|----------|-----------|
| `INVENTARIO_API_URL` | IP **do seu PC** onde o dashboard está rodando |
| `INVENTARIO_HTML=0` | Não abre HTML na máquina monitorada — os dados vão só pro seu dashboard |

Se der certo, a máquina aparece em `http://localhost:5000` no **seu** navegador.

### 3. Automatizar (recomendado)

Agende no **Agendador de Tarefas** do Windows para rodar todo dia (ou na inicialização):

- **Programa:** caminho do `inventario.exe`
- **Variáveis de ambiente na tarefa:**
  - `INVENTARIO_API_URL` = `http://SEU_IP:5000/api/inventario`
  - `INVENTARIO_HTML` = `0`

---

## Rotina do dia a dia

| Quando | O que fazer |
|--------|-------------|
| **Começar o dia** | Duplo clique em `iniciar-dashboard.bat` |
| **Ver inventário** | Navegador → `http://localhost:5000` |
| **Máquina nova** | Copiar `inventario.exe` + configurar com seu IP |
| **Atualizar o sistema** | Na pasta do projeto: `git pull` e rodar o `.bat` de novo |

---

## Problemas comuns

| Problema | Solução |
|----------|---------|
| "Python não encontrado" | Reinstalar Python com **Add to PATH** marcado |
| Máquina não aparece no dashboard | Dashboard está aberto? IP correto? Mesma rede? |
| Erro de conexão no agente | Firewall do Windows pode estar bloqueando a porta **5000** — liberar na rede interna |
| Dashboard vazio | Rodar o `inventario.exe` em pelo menos uma máquina com o IP certo |

### Liberar porta no firewall (se precisar)

No **seu PC**, no PowerShell como administrador:

```powershell
New-NetFirewallRule -DisplayName "Wadamy Dashboard" -Direction Inbound -Port 5000 -Protocol TCP -Action Allow
```

---

## Resumo em 3 linhas

1. **Você:** duplo clique em `iniciar-dashboard.bat` → abre `http://localhost:5000`
2. **Outras máquinas:** rodam `inventario.exe` apontando pro **seu IP**
3. **Só você** vê os dados — tudo fica no seu PC

---

Dúvidas técnicas: falar com o Marcos.
