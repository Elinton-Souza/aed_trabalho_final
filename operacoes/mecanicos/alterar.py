from psycopg2.extras import RealDictCursor
from rich.console import Console
from rich.prompt import Prompt

from db import get_connection

console = Console()


def alterar_mecanico():
    console.print("\n[bold yellow]Alteração de Mecânico[/bold yellow]")

    id_mecanico = Prompt.ask("ID do mecânico que deseja alterar")

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

            novo_nome = Prompt.ask(
                "Novo nome",
                default=mecanico["nome"]
            ).strip()

            if not novo_nome:
                console.print("[red]Nome não pode ser vazio.[/red]")
                return

            with conexao.cursor() as cursor:
                cursor.execute(
                    "UPDATE mecanicos SET nome = %s WHERE id = %s",
                    (novo_nome, id_mecanico)
                )
            conexao.commit()

        console.print(f"[green]Mecânico atualizado para '{novo_nome}'.[/green]")
    except Exception as erro:
        console.print(f"[red]Erro ao alterar: {erro}[/red]")
