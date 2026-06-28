import os
from datetime import datetime, date

from psycopg2.extras import RealDictCursor
from rich.console import Console
from rich.prompt import Prompt

import plotly.express as px
import pandas as pd

from db import get_connection

console = Console()

PASTA_GRAFICOS = "graficos"


def _primeiro_dia_mes_atras(meses_atras):
    hoje = date.today()
    ano = hoje.year
    mes = hoje.month - meses_atras
    while mes <= 0:
        mes += 12
        ano -= 1
    return date(ano, mes, 1)


def gerar_grafico():
    console.print("\n[bold magenta]Gerar Gráfico[/bold magenta]")
    console.print("1. Custo total por mecânico (barras)")
    console.print("2. Quantidade de serviços por mecânico (barras)")
    console.print("3. Custo total por placa (top 10)")
    opcao = Prompt.ask("Escolha", choices=["1", "2", "3"], default="1")

    console.print("\n[cyan]Período de análise:[/cyan]")
    console.print("  1. Histórico completo (desde o primeiro registro do veículo)")
    console.print("  2. Por mês (mês atual ou últimos N meses)")
    periodo_opcao = Prompt.ask("Escolha", choices=["1", "2"], default="2")

    filtro_data = ""
    parametros = ()
    sufixo_periodo = " (histórico completo)"

    if periodo_opcao == "2":
        meses_txt = Prompt.ask("Quantos meses (incluindo o atual)", default="1")
        try:
            meses = max(1, int(meses_txt))
        except ValueError:
            meses = 1

        data_corte = _primeiro_dia_mes_atras(meses - 1)
        filtro_data = "WHERE man.data_servico >= %s"
        parametros = (data_corte,)
        sufixo_periodo = (
            " (mês atual)" if meses == 1
            else f" (últimos {meses} meses, desde {data_corte.strftime('%d/%m/%Y')})"
        )

    if opcao == "1":
        sql = f"""
            SELECT mec.nome AS mecanico, SUM(man.custo) AS total
            FROM manutencoes man
            JOIN mecanicos mec ON mec.id = man.mecanico_id
            {filtro_data}
            GROUP BY mec.nome
            ORDER BY total DESC
        """
        titulo = "Custo total de manutenções por mecânico" + sufixo_periodo
        x, y = "mecanico", "total"
        rotulo_y = "Custo total (R$)"
    elif opcao == "2":
        sql = f"""
            SELECT mec.nome AS mecanico, COUNT(*) AS quantidade
            FROM manutencoes man
            JOIN mecanicos mec ON mec.id = man.mecanico_id
            {filtro_data}
            GROUP BY mec.nome
            ORDER BY quantidade DESC
        """
        titulo = "Quantidade de serviços por mecânico" + sufixo_periodo
        x, y = "mecanico", "quantidade"
        rotulo_y = "Nº de serviços"
    else:
        sql = f"""
            SELECT man.placa, SUM(man.custo) AS total
            FROM manutencoes man
            {filtro_data}
            GROUP BY man.placa
            ORDER BY total DESC
            LIMIT 10
        """
        titulo = "Top 10 placas com maior custo acumulado" + sufixo_periodo
        x, y = "placa", "total"
        rotulo_y = "Custo total (R$)"

    try:
        with get_connection() as conexao:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, parametros)
                dados = cursor.fetchall()
    except Exception as erro:
        console.print(f"[red]Erro ao buscar dados: {erro}[/red]")
        return

    if not dados:
        console.print("[yellow]Sem dados no período selecionado para gerar o gráfico.[/yellow]")
        return

    df = pd.DataFrame(dados)

    fig = px.bar(df, x=x, y=y, title=titulo, text_auto=True,
                 labels={x: x.capitalize(), y: rotulo_y})

    os.makedirs(PASTA_GRAFICOS, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo = os.path.join(PASTA_GRAFICOS, f"grafico_{opcao}_{timestamp}.html")
    fig.write_html(arquivo, auto_open=True)

    console.print(f"[green]Gráfico salvo e aberto:[/green] [bold]{arquivo}[/bold]")
