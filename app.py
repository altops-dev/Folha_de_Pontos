import json
import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for

from sheets_handler import SheetsHandler

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24)

DEMO_USERS = {
    "Ana": "1234",
    "Bruno": "5678",
    "Carla": "9012",
    "Diego": "3456",
}


def load_users():
    raw = os.environ.get("USERS_JSON", "").strip()
    if not raw:
        return DEMO_USERS
    try:
        users = json.loads(raw)
    except json.JSONDecodeError:
        print("USERS_JSON inválido no .env; a usar utilizadores de demonstração.")
        return DEMO_USERS
    if not isinstance(users, dict) or not users:
        return DEMO_USERS
    return {str(name): str(pin) for name, pin in users.items()}


USERS = load_users()
sheets = SheetsHandler()


@app.route("/")
def index():
    if "user" in session:
        return render_template("index.html", user=session["user"])
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome = request.form.get("nome")
        pin = request.form.get("pin")

        if nome in USERS and USERS[nome] == pin:
            session["user"] = nome
            return redirect(url_for("index"))
        flash("Nome ou PIN incorretos.", "danger")

    return render_template("login.html", users=USERS.keys())


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/registrar/<tipo>", methods=["POST"])
def registrar(tipo):
    if "user" not in session:
        return redirect(url_for("login"))

    nome = session["user"]
    sucesso, mensagem = sheets.registrar_ponto(nome, tipo)

    if sucesso:
        flash(mensagem, "success")
    else:
        flash(mensagem, "danger")

    return redirect(url_for("index"))


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=debug)
