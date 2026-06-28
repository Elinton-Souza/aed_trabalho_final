from psycopg2.extras import RealDictCursor
from rich.console import Console
from rich.prompt import Prompt, Confirm

from db import get_connection

console = Console()


def excluir_manutencao():
    console.print("\n[bold red]Exclusão de Manutenção[/bold red]")

    id_manutencao = Prompt.ask("ID da manutenção que deseja excluir")

    try:
        with get_connection() as conexao:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT descricao, placa, data_servico, custo "
                    "FROM manutencoes WHERE id = %s",
                    (id_manutencao,)
                )
                m = cursor.fetchone()

            if m is None:
                console.print("[red]Manutenção não encontrada.[/red]")
                return

            console.print(
                f"[yellow]Você está prestes a excluir:[/yellow] "
                f"[bold]{m['descricao']}[/bold] — placa {m['placa']} — "
                f"{m['data_servico'].strftime('%d/%m/%Y')} — R$ {m['custo']:.2f}"
            )
            if not Confirm.ask("Confirma a exclusão?", default=False):
                console.print("[cyan]Operação cancelada.[/cyan]")
                return

            with conexao.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM manutencoes WHERE id = %s",
                    (id_manutencao,)
                )
                removidos = cursor.rowcount
            conexao.commit()

        console.print(f"[green]{removidos} manutenção(ões) excluída(s).[/green]")
    except Exception as erro:
        console.print(f"[red]Erro ao excluir: {erro}[/red]")
