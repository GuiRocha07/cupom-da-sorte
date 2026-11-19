"""Banco SQLite: campanhas, participantes e ganhadores."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from .core import Participante

ESQUEMA = """
CREATE TABLE IF NOT EXISTS campanhas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    premios TEXT NOT NULL,          -- lista JSON, na ordem em que serão sorteados
    criada_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS participantes (
    campanha_id INTEGER NOT NULL REFERENCES campanhas(id),
    nome TEXT NOT NULL,
    codigo TEXT NOT NULL,
    cupons INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS ganhadores (
    campanha_id INTEGER NOT NULL REFERENCES campanhas(id),
    posicao INTEGER NOT NULL,
    premio TEXT NOT NULL,
    nome TEXT NOT NULL,
    codigo TEXT NOT NULL,
    cupons INTEGER NOT NULL,
    sorteado_em TEXT NOT NULL
);
"""


def conectar(caminho: str) -> sqlite3.Connection:
    con = sqlite3.connect(caminho)
    con.row_factory = sqlite3.Row
    con.executescript(ESQUEMA)
    return con


def criar_campanha(con: sqlite3.Connection, titulo: str, premios: list[str], participantes: list[Participante]) -> int:
    cur = con.execute(
        "INSERT INTO campanhas (titulo, premios, criada_em) VALUES (?, ?, ?)",
        (titulo, json.dumps(premios, ensure_ascii=False), datetime.now().isoformat(timespec="seconds")),
    )
    campanha_id = cur.lastrowid
    con.executemany(
        "INSERT INTO participantes (campanha_id, nome, codigo, cupons) VALUES (?, ?, ?, ?)",
        [(campanha_id, p.nome, p.codigo, p.cupons) for p in participantes],
    )
    con.commit()
    return campanha_id


def campanha_atual(con: sqlite3.Connection) -> sqlite3.Row | None:
    return con.execute("SELECT * FROM campanhas ORDER BY id DESC LIMIT 1").fetchone()


def campanha(con: sqlite3.Connection, campanha_id: int) -> sqlite3.Row | None:
    return con.execute("SELECT * FROM campanhas WHERE id = ?", (campanha_id,)).fetchone()


def premios(row: sqlite3.Row) -> list[str]:
    return json.loads(row["premios"])


def participantes(con: sqlite3.Connection, campanha_id: int) -> list[Participante]:
    rows = con.execute(
        "SELECT nome, codigo, cupons FROM participantes WHERE campanha_id = ? ORDER BY nome", (campanha_id,)
    ).fetchall()
    return [Participante(r["nome"], r["codigo"], r["cupons"]) for r in rows]


def ganhadores(con: sqlite3.Connection, campanha_id: int | None = None) -> list[sqlite3.Row]:
    sql = (
        "SELECT g.*, c.titulo FROM ganhadores g JOIN campanhas c ON c.id = g.campanha_id"
        + (" WHERE g.campanha_id = ?" if campanha_id else "")
        + " ORDER BY g.campanha_id DESC, g.posicao"
    )
    return con.execute(sql, (campanha_id,) if campanha_id else ()).fetchall()


def registrar_ganhador(con: sqlite3.Connection, campanha_id: int, posicao: int, premio: str, p: Participante) -> None:
    con.execute(
        "INSERT INTO ganhadores (campanha_id, posicao, premio, nome, codigo, cupons, sorteado_em)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (campanha_id, posicao, premio, p.nome, p.codigo, p.cupons, datetime.now().isoformat(timespec="seconds")),
    )
    con.commit()
