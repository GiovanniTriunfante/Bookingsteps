from flask import Flask, render_template, request, redirect, url_for, jsonify
from gerenciamento import GerenciamentoReservasSupabase
from datetime import date, timedelta

app = Flask(__name__)

# Configuração do Supabase
SUPABASE_URL = "https://eyixwisqnlfkbdzidcyl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV5aXh3aXNxbmxma2JkemlkY3lsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA4MzAzNDksImV4cCI6MjA0NjQwNjM0OX0.ORGFaR_DZS5wJCaPfLPJRTEHZkc85U-vx7aE1Dh5JPI"
reservas = GerenciamentoReservasSupabase(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def dashboard():
    """Página inicial com as reservas e imóveis listados."""
    reservas_ordenadas = reservas.buscar_reservas_com_imoveis(order_by="entrada")
    imoveis = reservas.fetch_table("imoveisbeta", order_by="numero_apto")
    return render_template(
        "dashboard.html",
        title="Dashboard",
        reservas=reservas_ordenadas,
        imoveis=imoveis
    )


@app.route("/reservas", methods=["GET", "POST"])
def reservas_route():
    """Página para listar e adicionar reservas."""
    if request.method == "POST":
        # Processar formulário de nova reserva
        data = request.form
        sucesso = reservas.adicionar_reserva(
            nome_hospede=data["nome_hospede"],
            entrada=data["entrada"],
            saida=data["saida"],
            imovel_id=data["imovel_id"],
            nome_parceiro=data["nome_parceiro"]
        )
        if sucesso:
            return redirect(url_for("reservas_route"))
        return render_template(
            "reservas.html",
            title="Reservas",
            reservas=reservas.buscar_reservas_com_imoveis(order_by="entrada"),
            error="Erro ao adicionar a reserva."
        )

    # Renderizar a página de reservas com a lista atual
    reservas_ordenadas = reservas.buscar_reservas_com_imoveis(order_by="entrada")
    return render_template("reservas.html", title="Reservas", reservas=reservas_ordenadas)


@app.route("/reservas/<int:id_reserva>", methods=["POST"])
def editar_reserva(id_reserva):
    """Editar uma reserva existente."""
    data = request.form
    sucesso = reservas.editar_reserva(
        id_reserva=id_reserva,
        nome_hospede=data.get("nome_hospede"),
        entrada=data.get("entrada"),
        saida=data.get("saida"),
        imovel_id=data.get("imovel_id"),
        nome_parceiro=data.get("nome_parceiro")
    )
    if sucesso:
        return redirect(url_for("reservas_route"))
    return render_template(
        "reservas.html",
        title="Reservas",
        reservas=reservas.buscar_reservas_com_imoveis(order_by="entrada"),
        error="Erro ao atualizar a reserva."
    )


@app.route("/imoveis", methods=["GET", "POST"])
def imoveis_route():
    """Página para listar e adicionar imóveis."""
    if request.method == "POST":
        # Processar formulário de novo imóvel
        data = request.form
        sucesso = reservas.adicionar_imovel(
            numero_apto=data["numero_apto"],
            bloco=data["bloco"],
            condominio=data["condominio"],
            proprietario=data["proprietario"]
        )
        if sucesso:
            return redirect(url_for("imoveis_route"))
        return render_template(
            "imoveis.html",
            title="Imóveis",
            imoveis=reservas.fetch_table("imoveisbeta", order_by="numero_apto"),
            error="Erro ao adicionar o imóvel."
        )

    # Renderizar a página de imóveis com a lista atual
    imoveis = reservas.fetch_table("imoveisbeta", order_by="numero_apto")
    return render_template("imoveis.html", title="Imóveis", imoveis=imoveis)


@app.route("/imoveis/<int:imovel_id>", methods=["POST"])
def editar_imovel(imovel_id):
    """Editar um imóvel existente."""
    data = request.form
    sucesso = reservas.editar_imovel(
        imovel_id=imovel_id,
        numero_apto=data.get("numero_apto"),
        bloco=data.get("bloco"),
        condominio=data.get("condominio"),
        proprietario=data.get("proprietario")
    )
    if sucesso:
        return redirect(url_for("imoveis_route"))
    return render_template(
        "imoveis.html",
        title="Imóveis",
        imoveis=reservas.fetch_table("imoveisbeta", order_by="numero_apto"),
        error="Erro ao atualizar o imóvel."
    )


if __name__ == "__main__":
    app.run(debug=True)
