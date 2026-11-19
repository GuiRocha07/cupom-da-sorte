import pytest

from app import criar_app


@pytest.fixture
def cliente(tmp_path):
    app = criar_app(str(tmp_path / "teste.db"))
    app.config["TESTING"] = True
    return app.test_client()


def criar_campanha(cliente, premios="TV\nAir fryer"):
    return cliente.post("/campanhas", data={"titulo": "Sorteio de teste", "premios": premios})


def test_sem_campanha_mostra_formulario(cliente):
    assert "Nova campanha" in cliente.get("/").get_data(as_text=True)


def test_sorteia_todos_os_premios_sem_repetir_ganhador(cliente):
    criar_campanha(cliente)
    primeiro = cliente.post("/campanhas/1/sortear").get_json()
    segundo = cliente.post("/campanhas/1/sortear").get_json()

    assert primeiro["premio"] == "TV" and segundo["premio"] == "Air fryer"
    assert primeiro["codigo"] != segundo["codigo"]
    assert segundo["restantes"] == 0

    terceiro = cliente.post("/campanhas/1/sortear")
    assert terceiro.status_code == 409


def test_historico_lista_os_ganhadores(cliente):
    criar_campanha(cliente, premios="Bicicleta")
    ganhador = cliente.post("/campanhas/1/sortear").get_json()
    assert ganhador["nome"] in cliente.get("/historico").get_data(as_text=True)


def test_campanha_sem_premio_e_recusada(cliente):
    resposta = criar_campanha(cliente, premios="  ")
    assert resposta.status_code == 302
    assert "Nova campanha" in cliente.get("/campanhas/nova").get_data(as_text=True)
