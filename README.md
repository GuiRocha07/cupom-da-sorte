# 🎟️ Cupom da Sorte

Sistema web de **sorteio ponderado por cupons** para campanhas de vendas: cada cupom é uma chance, e quem compra mais tem mais chances de ganhar.

> Projeto de portfólio inspirado num sistema real que desenvolvi para a empresa onde trabalho. O código foi escrito do zero, e todos os nomes e dados são fictícios.

## O problema

Em campanhas do tipo "a cada compra, um cupom", a equipe comercial precisa de um sorteio **justo**, **transparente** e que dê para fazer **ao vivo**, com:

- chance proporcional à quantidade de cupons de cada cliente;
- vários prêmios, sorteados numa ordem definida;
- nenhum cliente ganhando duas vezes na mesma campanha;
- registro de quem ganhou o quê, e quando.

## O que o sistema faz

- **Importa a planilha de participantes (CSV)** e soma os cupons de clientes repetidos. Aceita uma linha por cliente (com a coluna "Cupons") ou uma linha por cupom.
- **Sorteio ponderado**: um cliente com 10 cupons tem 10 vezes mais chance que um com 1 cupom.
- **Prêmios em ordem**, e quem já ganhou sai do sorteio dos próximos prêmios.
- **Tela de apresentação** com tambor animado (nomes girando desfocados até revelar o ganhador), confete, e lista de participantes desfocada para preservar os dados dos clientes.
- **Histórico** de todos os ganhadores, salvo em banco SQLite.

## Tecnologias

Python 3 · Flask · SQLite · Jinja2 · JavaScript · CSS · pytest

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate      # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abra http://localhost:5000, crie uma campanha (sem enviar arquivo, ele usa `data/participantes_exemplo.csv`) e clique em **Sortear**.

## Testes

```bash
pytest
```

Os testes cobrem a leitura da planilha, a proporcionalidade do sorteio, a exclusão de quem já ganhou e o fluxo completo pela API.

## Estrutura

```
app.py                  rotas da aplicação Flask
sorteio/core.py         regras: leitura do CSV e sorteio ponderado
sorteio/db.py           banco SQLite (campanhas, participantes, ganhadores)
templates/              páginas HTML
static/                 estilo e animação do tambor
data/                   planilha de exemplo (dados fictícios)
tests/                  testes automatizados
```

## Autor

Feito por **Gui Rocha**: [LinkedIn](https://www.linkedin.com/in/guilherme-rochaaa) · [GitHub](https://github.com/GuiRocha07)
