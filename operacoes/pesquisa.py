from datetime import datetime

from psycopg2.extras import RealDictCursor
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from db import get_connection

console = Console()


def pesquisa_avancada():
    console.print("\n[bold blue]Pesquisa Avançada de Manutenções[/bold blue]")
    console.print("[dim]Deixe em branco (Enter) qualquer filtro que não queira aplicar.[/dim]\n")

    placa = Prompt.ask("Placa (parte do texto)", default="").strip().upper()
    data_inicio_txt = Prompt.ask("Data inicial (AAAA-MM-DD)", default="").strip()
    data_fim_txt = Prompt.ask("Data final (AAAA-MM-DD)", default="").strip()
    custo_min_txt = Prompt.ask("Custo mínimo (R$)", default="").strip()

    try:
        with get_connection() as conexao:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, nome FROM mecanicos ORDER BY nome")
                mecanicos = cursor.fetchall()
    except Exception as erro:
        console.print(f"[red]Erro ao listar mecânicos: {erro}[/red]")
        return

    console.print("\n[cyan]Mecânicos disponíveis:[/cyan]")
    console.print("  [bold] 0[/bold] - Qualquer (sem filtro)")
    for mec in mecanicos:
        console.print(f"  [bold]{mec['id']:>2}[/bold] - {mec['nome']}")
    ids_validos = ["0"] + [str(m["id"]) for m in mecanicos]
    mecanico_id_txt = Prompt.ask("ID do mecânico", choices=ids_validos, default="0")

    condicoes = []
    valores = []

    if placa:
        condicoes.append("man.placa ILIKE %s")
        valores.append(f"%{placa}%")

    if data_inicio_txt:
        try:
            data_inicio = datetime.strptime(data_inicio_txt, "%Y-%m-%d").date()
            condicoes.append("man.data_servico >= %s")
            valores.append(data_inicio)
        except ValueError:
            console.print("[red]Data inicial inválida — ignorada.[/red]")

    if data_fim_txt:
        try:
            data_fim = datetime.strptime(data_fim_txt, "%Y-%m-%d").date()
            condicoes.append("man.data_servico <= %s")
            valores.append(data_fim)
        except ValueError:
            console.print("[red]Data final inválida — ignorada.[/red]")

    if custo_min_txt:
        try:
            custo_min = float(custo_min_txt)
            condicoes.append("man.custo >= %s")
            valores.append(custo_min)
        except ValueError:
            console.print("[red]Custo mínimo inválido — ignorado.[/red]")

    if mecanico_id_txt != "0":
        condicoes.append("man.mecanico_id = %s")
        valores.append(int(mecanico_id_txt))

    where_sql = " AND ".join(condicoes) if condicoes else "1=1"

    sql = f"""
        SELECT man.id, man.descricao, man.placa, man.data_servico, man.custo, mec.nome AS mecanico
        FROM manutencoes man
        JOIN mecanicos mec ON mec.id = man.mecanico_id
        WHERE {where_sql}
        ORDER BY man.data_servico DESC
    """

    try:
        with get_connection() as conexao:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, tuple(valores))
                resultados = cursor.fetchall()
    except Exception as erro:
        console.print(f"[red]Erro na consulta: {erro}[/red]")
        return

    if not resultados:
        console.print("[yellow]Nenhuma manutenção encontrada com esses filtros.[/yellow]")
        return

    tabela = Table(title=f"Resultados ({len(resultados)} encontrada(s))")
    tabela.add_column("ID", justify="right", style="cyan")
    tabela.add_column("Descrição")
    tabela.add_column("Placa", style="yellow")
    tabela.add_column("Data", style="green")
    tabela.add_column("Custo", justify="right", style="magenta")
    tabela.add_column("Mecânico", style="blue")

    for r in resultados:
        tabela.add_row(
            str(r["id"]),
            r["descricao"],
            r["placa"],
            r["data_servico"].strftime("%d/%m/%Y"),
            f"R$ {r['custo']:>9.2f}",
            r["mecanico"],
        )

    console.print(tabela)
