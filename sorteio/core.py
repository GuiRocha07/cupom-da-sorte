"""Regras do sorteio: leitura da planilha de cupons e sorteio ponderado.

Cada cupom é uma chance. Um cliente com 5 cupons tem 5 vezes mais chance
que um cliente com 1 cupom. Quem já ganhou não concorre de novo na mesma campanha.
"""

from __future__ import annotations

import csv
import io
import random
import unicodedata
from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass
class Participante:
    nome: str
    codigo: str
    cupons: int

    @property
    def chave(self) -> str:
        """Identifica o cliente: pelo código, ou pelo nome quando não há código."""
        if self.codigo:
            return f"codigo:{self.codigo}"
        return f"nome:{normalizar(self.nome)}"


def normalizar(texto: object) -> str:
    """Tira acentos, espaços das pontas e deixa minúsculo ("Código " -> "codigo")."""
    texto = unicodedata.normalize("NFD", str(texto or "").strip())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn").lower()


class PlanilhaInvalida(ValueError):
    """A planilha não tem as colunas esperadas ou tem um valor errado."""


COLUNAS_NOME = {"nome", "nome fantasia", "nome do cliente", "cliente"}
COLUNAS_CODIGO = {"codigo", "cod. cliente", "codigo do cliente", "cod cliente"}
COLUNAS_CUPONS = {"cupons", "qtd cupons", "quantidade de cupons"}


def _indice(cabecalho: list[str], opcoes: set[str]) -> int:
    for i, coluna in enumerate(cabecalho):
        if coluna in opcoes:
            return i
    return -1


def ler_csv(texto: str) -> list[Participante]:
    """Lê o CSV de participantes e soma os cupons de quem aparece mais de uma vez.

    Aceita dois formatos:
    - uma linha por cliente, com a coluna "Cupons";
    - uma linha por cupom (sem a coluna "Cupons"): cada linha vale 1 cupom.
    """
    linhas = list(csv.reader(io.StringIO(texto.lstrip("\ufeff"))))
    if not linhas:
        raise PlanilhaInvalida("A planilha está vazia.")

    cabecalho = [normalizar(c) for c in linhas[0]]
    i_nome = _indice(cabecalho, COLUNAS_NOME)
    i_codigo = _indice(cabecalho, COLUNAS_CODIGO)
    i_cupons = _indice(cabecalho, COLUNAS_CUPONS)
    if i_nome < 0:
        raise PlanilhaInvalida('A planilha precisa de uma coluna "Nome".')

    clientes: dict[str, Participante] = {}
    for numero_linha, linha in enumerate(linhas[1:], start=2):
        nome = linha[i_nome].strip() if i_nome < len(linha) else ""
        if not nome:
            continue
        codigo = linha[i_codigo].strip() if 0 <= i_codigo < len(linha) else ""

        if i_cupons < 0:
            cupons = 1
        else:
            bruto = linha[i_cupons].strip() if i_cupons < len(linha) else ""
            try:
                cupons = int(bruto.replace(",", ".").split(".")[0] or "0")
            except ValueError:
                raise PlanilhaInvalida(
                    f"Linha {numero_linha}: quantidade de cupons inválida para {nome}."
                ) from None
            if cupons < 0:
                raise PlanilhaInvalida(f"Linha {numero_linha}: cupons negativos para {nome}.")

        p = Participante(nome=nome, codigo=codigo, cupons=cupons)
        if p.chave in clientes:
            clientes[p.chave].cupons += cupons
        else:
            clientes[p.chave] = p
    return list(clientes.values())


def total_cupons(lista: Iterable[Participante]) -> int:
    return sum(p.cupons for p in lista)


def disponiveis(lista: list[Participante], ganhadores_chaves: set[str]) -> list[Participante]:
    """Quem ainda pode ganhar: tem cupom e não ganhou nesta campanha."""
    return [p for p in lista if p.cupons > 0 and p.chave not in ganhadores_chaves]


def sortear(lista: list[Participante], aleatorio: Callable[[], float] = random.random) -> Participante | None:
    """Sorteia um participante com chance proporcional aos cupons."""
    total = total_cupons(lista)
    if total <= 0:
        return None
    bilhete = aleatorio() * total
    for p in lista:
        bilhete -= p.cupons
        if bilhete < 0:
            return p
    return lista[-1]
