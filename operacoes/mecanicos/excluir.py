from psycopg2.extras import RealDictCursor
from rich.console import Console
from rich.prompt import Prompt, Confirm

from db import get_connection

console = Console()


def excluir_mecanico():
    console.print("\n[bold red]Exclusão de Mecânico[/bold red]")

    id_mecanico = Prompt.ask("ID do mecânico que deseja excluir")

    try:
        with get_connection() as conexao:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT id, nome FROM mecanicos WHERE id = %s",
                    (id_mecanico,)
                )
                mecanico = cursor.fetchone()

            if mecanico is None:
                console.print("[red]Mecânico não encontrado.[/red]")
                return

            with conexao.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM manutencoes WHERE mecanico_id = %s",
                    (id_mecanico,)
                )
                qtd_manutencoes = cursor.fetchone()[0]

            console.print(
                f"[yellow]Atenção:[/yellow] mecânico [bold]{mecanico['nome']}[/bold] "
                f"tem [bold]{qtd_manutencoes}[/bold] manutenção(ões) vinculada(s) "
                "que serão apagadas junto e registradas no histórico."
            )
            if not Confirm.ask("Confirma a exclusão?", default=False):
                console.print("[cyan]Operação cancelada.[/cyan]")
                return

            with conexao.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM mecanicos WHERE id = %s",
                    (id_mecanico,)
                )
                removidos = cursor.rowcount
            conexao.commit()

        console.print(f"[green]{removidos} mecânico(s) excluído(s) com sucesso.[/green]")
    except Exception as erro:
        console.print(f"[red]Erro ao excluir: {erro}[/red]")
