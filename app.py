"""Cupom da Sorte: aplicação web do sorteio.

Rodar:  python app.py   e abrir http://localhost:5000
"""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, flash, g, jsonify, redirect, render_template, request, url_for

from sorteio import db
from sorteio.core import Participante, PlanilhaInvalida, disponiveis, ler_csv, sortear, total_cupons

PASTA = Path(__file__).parent
EXEMPLO_CSV = PASTA / "data" / "participantes_exemplo.csv"


def criar_app(caminho_banco: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "troque-esta-chave")
    app.config["BANCO"] = caminho_banco or os.environ.get("BANCO", str(PASTA / "sorteio.db"))

    def con():
        if "con" not in g:
            g.con = db.conectar(app.config["BANCO"])
        return g.con

    @app.teardown_appcontext
    def fechar(_erro):
        conexao = g.pop("con", None)
        if conexao is not None:
            conexao.close()

    @app.get("/")
    def inicio():
        atual = db.campanha_atual(con())
        if atual is None:
            return render_template("nova_campanha.html")
        lista = db.participantes(con(), atual["id"])
        vencedores = db.ganhadores(con(), atual["id"])
        lista_premios = db.premios(atual)
        return render_template(
            "sorteio.html",
            campanha=atual,
            participantes=lista,
            total=total_cupons(lista),
            ganhadores=vencedores,
            premios=lista_premios,
            proximo_premio=lista_premios[len(vencedores)] if len(vencedores) < len(lista_premios) else None,
        )

    @app.get("/campanhas/nova")
    def nova_campanha():
        return render_template("nova_campanha.html")

    @app.post("/campanhas")
    def criar_campanha():
        titulo = request.form.get("titulo", "").strip() or "Sorteio"
        premios = [p.strip() for p in request.form.get("premios", "").splitlines() if p.strip()]
        if not premios:
            flash("Informe pelo menos um prêmio.")
            return redirect(url_for("nova_campanha"))

        arquivo = request.files.get("planilha")
        if arquivo and arquivo.filename:
            texto = arquivo.read().decode("utf-8-sig")
        else:
            texto = EXEMPLO_CSV.read_text(encoding="utf-8")

        try:
            lista = ler_csv(texto)
        except PlanilhaInvalida as erro:
            flash(str(erro))
            return redirect(url_for("nova_campanha"))
        if total_cupons(lista) == 0:
            flash("Nenhum participante tem cupom.")
            return redirect(url_for("nova_campanha"))

        db.criar_campanha(con(), titulo, premios, lista)
        return redirect(url_for("inicio"))

    @app.post("/campanhas/<int:campanha_id>/sortear")
    def sortear_premio(campanha_id: int):
        atual = db.campanha(con(), campanha_id)
        if atual is None:
            return jsonify(erro="Campanha não encontrada."), 404

        lista_premios = db.premios(atual)
        vencedores = db.ganhadores(con(), campanha_id)
        if len(vencedores) >= len(lista_premios):
            return jsonify(erro="Todos os prêmios já foram sorteados."), 409

        ja_ganharam = {Participante(v["nome"], v["codigo"], v["cupons"]).chave for v in vencedores}
        concorrendo = disponiveis(db.participantes(con(), campanha_id), ja_ganharam)
        ganhador = sortear(concorrendo)
        if ganhador is None:
            return jsonify(erro="Não há mais participantes com cupons."), 409

        posicao = len(vencedores) + 1
        premio = lista_premios[posicao - 1]
        db.registrar_ganhador(con(), campanha_id, posicao, premio, ganhador)
        return jsonify(
            posicao=posicao,
            premio=premio,
            nome=ganhador.nome,
            codigo=ganhador.codigo,
            cupons=ganhador.cupons,
            restantes=len(lista_premios) - posicao,
            nomes_tambor=[p.nome for p in concorrendo],
        )

    @app.get("/historico")
    def historico():
        return render_template("historico.html", ganhadores=db.ganhadores(con()))

    return app


app = criar_app()

if __name__ == "__main__":
    app.run(debug=True)
