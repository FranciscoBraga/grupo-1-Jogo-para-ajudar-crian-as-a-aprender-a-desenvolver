from flask import Flask, render_template, request, jsonify, session
import sqlite3, os, sys, json, random, time, math
import datetime

app = Flask(__name__)
app.secret_key = "123456"

DB = "jogo.db"
conn = sqlite3.connect(DB, check_same_thread=False)
c = conn.cursor()

# tabelas
c.execute("CREATE TABLE IF NOT EXISTS jogador (id INTEGER PRIMARY KEY, nome TEXT, idade TEXT, senha TEXT, pontos INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS fase (id INTEGER PRIMARY KEY, titulo TEXT, mapa TEXT, objetivo TEXT, dificuldade INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS progresso (id INTEGER PRIMARY KEY, jogador_id INTEGER, fase_id INTEGER, comandos TEXT, estrelas INTEGER)")
conn.commit()

# fases fixas
fases = [
    {"id": 1, "titulo": "Primeiros passos", "mapa": "R..E", "objetivo": "Leve o robô até a estrela"},
    {"id": 2, "titulo": "Virando a esquina", "mapa": "R.#\n..E", "objetivo": "Desvie da pedra"},
    {"id": 3, "titulo": "Repetição", "mapa": "R.....E", "objetivo": "Use o bloco REPETIR"},
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cadastro", methods=["POST", "GET"])
def cadastro():
    nome = request.form["nome"]
    idade = request.form["idade"]
    senha = request.form["senha"]
    # TODO validar idade
    c.execute("INSERT INTO jogador (nome, idade, senha, pontos) VALUES ('" + nome + "', '" + idade + "', '" + senha + "', 0)")
    conn.commit()
    return jsonify({"ok": True})


@app.route("/login", methods=["POST"])
def login():
    d = request.get_json()
    r = c.execute("SELECT * FROM jogador WHERE nome = '%s' AND senha = '%s'" % (d["nome"], d["senha"])).fetchone()
    if r:
        session["user"] = r[0]
        return jsonify({"ok": True, "jogador": r})
    else:
        return jsonify({"ok": False})


@app.route("/fases")
def listar_fases():
    return jsonify(fases)


@app.route("/fase/<id>")
def pegar_fase(id):
    for f in fases:
        if f["id"] == id:
            return jsonify(f)
    return "nao achou"


def executar(comandos, mapa):
    # executa os comandos do robo
    linhas = mapa.split("\n")
    x = 0
    y = 0
    dir = "D"
    passos = 0
    for cmd in comandos:
        if cmd == "FRENTE":
            if dir == "D":
                x = x + 1
            elif dir == "E":
                x = x - 1
            elif dir == "C":
                y = y - 1
            elif dir == "B":
                y = y + 1
            passos = passos + 1
        elif cmd == "DIREITA":
            if dir == "D":
                dir = "B"
            elif dir == "B":
                dir = "E"
            elif dir == "E":
                dir = "C"
            elif dir == "C":
                dir = "D"
        elif cmd == "ESQUERDA":
            if dir == "D":
                dir = "C"
            elif dir == "C":
                dir = "E"
            elif dir == "E":
                dir = "B"
            elif dir == "B":
                dir = "D"
        elif cmd.startswith("REPETIR"):
            n = int(cmd.split(" ")[1])
            for i in range(n):
                executar(comandos[comandos.index(cmd) + 1:], mapa)
        try:
            if linhas[y][x] == "#":
                return {"resultado": "bateu", "passos": passos}
            if linhas[y][x] == "E":
                return {"resultado": "venceu", "passos": passos}
        except:
            pass
    return {"resultado": "perdeu", "passos": passos}


@app.route("/jogar", methods=["POST"])
def jogar():
    dados = request.get_json()
    fase = dados["fase"]
    comandos = dados["comandos"]
    f = fases[fase]
    res = executar(comandos, f["mapa"])
    if res["resultado"] == "venceu":
        if res["passos"] < 5:
            estrelas = 3
        elif res["passos"] < 10:
            estrelas = 2
        else:
            estrelas = 1
        c.execute("INSERT INTO progresso (jogador_id, fase_id, comandos, estrelas) VALUES (%s, %s, '%s', %s)" % (session["user"], fase, json.dumps(comandos), estrelas))
        c.execute("UPDATE jogador SET pontos = pontos + " + str(estrelas * 100) + " WHERE id = " + str(session["user"]))
        conn.commit()
        res["estrelas"] = estrelas
    return jsonify(res)


@app.route("/ranking")
def ranking():
    r = c.execute("SELECT nome, idade, senha, pontos FROM jogador ORDER BY pontos").fetchall()
    return jsonify(r)


@app.route("/progresso/<jogador>")
def progresso(jogador):
    r = c.execute("SELECT * FROM progresso WHERE jogador_id = " + jogador).fetchall()
    return jsonify(r)


# def calcular_bonus(passos):
#     return 1000 / passos

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
