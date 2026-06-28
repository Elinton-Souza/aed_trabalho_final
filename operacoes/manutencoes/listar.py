from psycopg2.extras import RealDictCursor
from rich.console import Console
from rich.table import Table

from db import get_connection

console = Console()


def listar_manutencoes():
    try:
        with get_connection() as conexao:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT
                        man.id,
                        man.descricao,
                        man.placa,
                        man.data_servico,
                        man.custo,
                        mec.nome AS mecanico
                    FROM manutencoes man
                    JOIN mecanicos mec ON mec.id = man.mecanico_id
                    ORDER BY man.data_servico DESC
                """)
                manutencoes = cursor.fetchall()
    except Exception as erro:
        console.print(f"[red]Erro ao buscar manutenções: {erro}[/red]")
        return

    if not manutencoes:
        console.print("[yellow]Nenhuma manutenção cadastrada.[/yellow]")
        return

    tabela = Table(title="Manutenções cadastradas")
    tabela.add_column("ID", justify="right", style="cyan")
    tabela.add_column("Descrição", style="white")
    tabela.add_column("Placa", style="yellow")
    tabela.add_column("Data", style="green")
    tabela.add_column("Custo", justify="right", style="magenta")
    tabela.add_column("Mecânico", style="blue")

    for m in manutencoes:
        tabela.add_row(
            str(m["id"]),
            m["descricao"],
            m["placa"],
            m["data_servico"].strftime("%d/%m/%Y"),
            f"R$ {m['custo']:>9.2f}",
            m["mecanico"],
        )

    console.print(tabela)
