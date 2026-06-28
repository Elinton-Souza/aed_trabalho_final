from psycopg2.extras import RealDictCursor
from rich.console import Console
from rich.table import Table

from db import get_connection

console = Console()


def listar_mecanicos():
    try:
        with get_connection() as conexao:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, nome FROM mecanicos ORDER BY nome")
                mecanicos = cursor.fetchall()
    except Exception as erro:
        console.print(f"[red]Erro ao buscar mecânicos: {erro}[/red]")
        return

    if not mecanicos:
        console.print("[yellow]Nenhum mecânico cadastrado.[/yellow]")
        return

    tabela = Table(title="Mecânicos cadastrados")
    tabela.add_column("ID", justify="right", style="cyan")
    tabela.add_column("Nome", style="magenta")

    for mecanico in mecanicos:
        tabela.add_row(str(mecanico["id"]), mecanico["nome"])

    console.print(tabela)
