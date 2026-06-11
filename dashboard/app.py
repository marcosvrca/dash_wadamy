import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("INVENTARIO_DB", BASE_DIR / "inventario.db"))

app = Flask(__name__)


def conectar():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    with conectar() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS maquinas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hostname TEXT NOT NULL,
                sistema TEXT,
                cpu TEXT,
                ram_gb REAL,
                ram_livre REAL,
                disco_gb REAL,
                disco_livre REAL,
                ip TEXT,
                cores INTEGER,
                coletado_em TEXT NOT NULL,
                recebido_em TEXT NOT NULL
            )
            """
        )
        conexao.execute(
            "CREATE INDEX IF NOT EXISTS idx_maquinas_hostname ON maquinas(hostname)"
        )


def validar_payload(dados):
    obrigatorios = ("hostname", "sistema", "cpu", "ip", "cores")
    faltando = [campo for campo in obrigatorios if campo not in dados]
    if faltando:
        return False, f"Campos obrigatórios ausentes: {', '.join(faltando)}"
    return True, None


@app.route("/")
def index():
    with conectar() as conexao:
        maquinas = conexao.execute(
            """
            SELECT m.*
            FROM maquinas m
            INNER JOIN (
                SELECT hostname, MAX(id) AS ultimo_id
                FROM maquinas
                GROUP BY hostname
            ) ultimos ON m.id = ultimos.ultimo_id
            ORDER BY m.hostname ASC
            """
        ).fetchall()

        total_registros = conexao.execute("SELECT COUNT(*) FROM maquinas").fetchone()[0]

    return render_template(
        "index.html",
        maquinas=maquinas,
        total_registros=total_registros,
        total_maquinas=len(maquinas),
    )


@app.route("/api/inventario", methods=["POST"])
def receber_inventario():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "JSON inválido"}), 400

    valido, mensagem = validar_payload(dados)
    if not valido:
        return jsonify({"erro": mensagem}), 400

    recebido_em = datetime.now(timezone.utc).isoformat()
    coletado_em = dados.get("coletado_em", recebido_em)

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO maquinas (
                hostname, sistema, cpu, ram_gb, ram_livre,
                disco_gb, disco_livre, ip, cores, coletado_em, recebido_em
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dados["hostname"],
                dados.get("sistema"),
                dados.get("cpu"),
                dados.get("ram_gb"),
                dados.get("ram_livre"),
                dados.get("disco_gb"),
                dados.get("disco_livre"),
                dados.get("ip"),
                dados.get("cores"),
                coletado_em,
                recebido_em,
            ),
        )
        registro_id = cursor.lastrowid

    return jsonify({"ok": True, "id": registro_id}), 201


@app.route("/api/maquinas")
def listar_maquinas():
    with conectar() as conexao:
        maquinas = conexao.execute(
            """
            SELECT m.*
            FROM maquinas m
            INNER JOIN (
                SELECT hostname, MAX(id) AS ultimo_id
                FROM maquinas
                GROUP BY hostname
            ) ultimos ON m.id = ultimos.ultimo_id
            ORDER BY m.hostname ASC
            """
        ).fetchall()

    return jsonify([dict(maquina) for maquina in maquinas])


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


inicializar_banco()

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta, debug=os.environ.get("FLASK_DEBUG") == "1")
