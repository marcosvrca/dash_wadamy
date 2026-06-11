import json
import os
import platform
import socket
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

import psutil

API_URL = os.environ.get("INVENTARIO_API_URL", "http://localhost:5000/api/inventario")
GERAR_HTML_LOCAL = os.environ.get("INVENTARIO_HTML", "1") == "1"


def obter_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def obter_cpu():
    sistema = platform.system()

    if sistema == "Windows":
        return platform.processor() or platform.machine()

    if sistema == "Linux":
        try:
            with open("/proc/cpuinfo", "r", encoding="utf-8") as arquivo:
                for linha in arquivo:
                    if "model name" in linha:
                        return linha.split(":")[1].strip()
        except OSError:
            pass

    if sistema == "Darwin":
        try:
            import subprocess

            resultado = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
                check=True,
            )
            return resultado.stdout.strip()
        except Exception:
            pass

    return platform.machine()


def obter_disco_raiz():
    if platform.system() == "Windows":
        return os.environ.get("SystemDrive", "C:") + "\\"
    return "/"


def coletar_dados():
    disco = psutil.disk_usage(obter_disco_raiz())
    memoria = psutil.virtual_memory()

    return {
        "hostname": socket.gethostname(),
        "sistema": f"{platform.system()} {platform.release()}",
        "cpu": obter_cpu(),
        "ram_gb": round(memoria.total / (1024**3), 2),
        "ram_livre": round(memoria.available / (1024**3), 2),
        "disco_gb": round(disco.total / (1024**3), 2),
        "disco_livre": round(disco.free / (1024**3), 2),
        "ip": obter_ip(),
        "cores": psutil.cpu_count(logical=True),
        "coletado_em": datetime.now(timezone.utc).isoformat(),
    }


def gerar_html(dados):
    linhas = [
        ("Hostname", dados["hostname"]),
        ("Sistema", dados["sistema"]),
        ("CPU", dados["cpu"]),
        ("Núcleos", dados["cores"]),
        ("RAM Total", f"{dados['ram_gb']} GB"),
        ("RAM Livre", f"{dados['ram_livre']} GB"),
        ("Disco Total", f"{dados['disco_gb']} GB"),
        ("Disco Livre", f"{dados['disco_livre']} GB"),
        ("IP", dados["ip"]),
    ]

    corpo = "\n".join(
        f"""
<div class="linha">
    <span class="label">{rotulo}:</span>
    <span class="valor">{valor}</span>
</div>"""
        for rotulo, valor in linhas
    )

    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Inventário da Máquina</title>
<style>
body {{
    font-family: Arial, sans-serif;
    background: #f4f6f9;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    margin: 0;
}}
.card {{
    background: white;
    width: min(700px, 92vw);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.15);
}}
h1 {{
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}}
.linha {{
    display: flex;
    justify-content: space-between;
    gap: 16px;
    margin: 12px 0;
    font-size: 16px;
}}
.label {{
    font-weight: bold;
    color: #7f8c8d;
}}
.valor {{
    color: #2c3e50;
    text-align: right;
}}
</style>
</head>
<body>
<div class="card">
<h1>Inventário da Máquina</h1>
{corpo}
</div>
</body>
</html>"""


def salvar_html_local(dados):
    arquivo_html = os.path.join(os.path.expanduser("~"), "inventario.html")
    with open(arquivo_html, "w", encoding="utf-8") as arquivo:
        arquivo.write(gerar_html(dados))
    return arquivo_html


def enviar_para_api(dados):
    try:
        import urllib.error
        import urllib.request

        requisicao = urllib.request.Request(
            API_URL,
            data=json.dumps(dados).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(requisicao, timeout=15) as resposta:
            return 200 <= resposta.status < 300
    except Exception as erro:
        print(f"Erro ao enviar para API ({API_URL}): {erro}")
        return False


def main():
    dados = coletar_dados()
    print(json.dumps(dados, indent=2, ensure_ascii=False))

    enviado = enviar_para_api(dados)
    if enviado:
        print(f"Dados enviados para: {API_URL}")
    else:
        print("Não foi possível enviar os dados para a API.")

    if GERAR_HTML_LOCAL:
        arquivo_html = salvar_html_local(dados)
        print(f"Arquivo criado: {arquivo_html}")
        try:
            webbrowser.open(Path(arquivo_html).as_uri())
        except Exception as erro:
            print(f"Erro ao abrir navegador: {erro}")

    if not enviado:
        print("Aviso: dados não foram enviados para a API.")

    sys.exit(0)


if __name__ == "__main__":
    main()
