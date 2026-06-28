from rich.console import Console
from rich.prompt import Prompt

from db import get_connection

console = Console()


def incluir_mecanico():
    console.print("\n[bold green]Inclusão de Mecânico[/bold green]")

    nome = Prompt.ask("Nome do mecânico").strip()

    if not nome:
        console.print("[red]Nome não pode ser vazio.[/red]")
        return

    try:
        with get_connection() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO mecanicos (nome) VALUES (%s)",
                    (nome,)
                )
            conexao.commit()
        console.print(f"[green]Mecânico '{nome}' cadastrado com sucesso![/green]")
    except Exception as erro:
        console.print(f"[red]Erro ao cadastrar: {erro}[/red]")
