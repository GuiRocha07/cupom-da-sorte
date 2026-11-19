import pytest

from sorteio.core import Participante, PlanilhaInvalida, disponiveis, ler_csv, sortear, total_cupons


def test_le_csv_e_soma_cupons_do_mesmo_cliente():
    texto = "Nome,Código,Cupons\nLoja A,1,3\nLoja B,2,1\nLoja A,1,2\n"
    lista = ler_csv(texto)
    assert len(lista) == 2
    assert {p.nome: p.cupons for p in lista} == {"Loja A": 5, "Loja B": 1}


def test_csv_sem_coluna_cupons_conta_uma_linha_por_cupom():
    texto = "Nome do cliente,Código do cliente,Pedido\nLoja A,1,100\nLoja A,1,101\nLoja B,2,102\n"
    lista = ler_csv(texto)
    assert {p.nome: p.cupons for p in lista} == {"Loja A": 2, "Loja B": 1}


def test_csv_sem_coluna_nome_da_erro():
    with pytest.raises(PlanilhaInvalida):
        ler_csv("Código,Cupons\n1,2\n")


def test_cupom_invalido_da_erro_com_a_linha():
    with pytest.raises(PlanilhaInvalida, match="Linha 2"):
        ler_csv("Nome,Cupons\nLoja A,muitos\n")


def test_sorteio_e_proporcional_aos_cupons():
    lista = [Participante("A", "1", 1), Participante("B", "2", 3)]
    # total = 4 cupons: bilhete < 1 cai em A, de 1 a 4 cai em B
    assert sortear(lista, lambda: 0.10).nome == "A"
    assert sortear(lista, lambda: 0.30).nome == "B"
    assert sortear(lista, lambda: 0.99).nome == "B"


def test_quem_ja_ganhou_nao_concorre_de_novo():
    a, b = Participante("A", "1", 5), Participante("B", "2", 0)
    c = Participante("C", "3", 2)
    restantes = disponiveis([a, b, c], {a.chave})
    assert restantes == [c]  # A já ganhou e B não tem cupom


def test_sem_cupons_nao_sorteia_ninguem():
    assert sortear([]) is None
    assert total_cupons([Participante("A", "1", 0)]) == 0
