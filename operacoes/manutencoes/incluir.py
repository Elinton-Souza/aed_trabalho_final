from datetime import datetime, date

from psycopg2.extras import RealDictCursor
from rich.console import Console
from rich.prompt import Prompt

from db import get_connection

console = Console()


def _listar_mecanicos_disponiveis(cursor):
    cursor.execute("SELECT id, nome FROM mecanicos ORDER BY nome")
    return cursor.fetchall()


def incluir_manutencao():
    console.print("\n[bold green]Inclusão de Manutenção[/bold green]")

    try:
        with get_connection() as conexao:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                mecanicos = _listar_mecanicos_disponiveis(cursor)

            if not mecanicos:
                console.print("[red]Nenhum mecânico cadastrado. Cadastre um primeiro.[/red]")
                return

            descricao = Prompt.ask("Descrição do serviço").strip()
            placa = Prompt.ask("Placa do veículo").strip().upper()

            data_texto = Prompt.ask(
                "Data do serviço (AAAA-MM-DD)",
                default=date.today().isoformat()
            )
            try:
                data_servico = datetime.strptime(data_texto, "%Y-%m-%d").date()
            except ValueError:
                console.print("[red]Data inválida. Use o formato AAAA-MM-DD.[/red]")
                return

            custo_texto = Prompt.ask("Custo (R$)", default="0.00")
            try:
                custo = float(custo_texto)
            except ValueError:
                console.print("[red]Custo inválido.[/red]")
                return
            if custo < 0:
                console.print("[red]Custo não pode ser negativo.[/red]")
                return

            console.print("\n[cyan]Mecânicos disponíveis:[/cyan]")
            for m in mecanicos:
                console.print(f"  [bold]{m['id']:>2}[/bold] - {m['nome']}")

            ids_validos = [str(m["id"]) for m in mecanicos]
            mecanico_id = Prompt.ask("ID do mecânico responsável", choices=ids_validos)

            with conexao.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO manutencoes (descricao, placa, data_servico, custo, mecanico_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (descricao, placa, data_servico, custo, int(mecanico_id))
                )
            conexao.commit()

        console.print(f"[green]Manutenção cadastrada com sucesso![/green]")
    except Exception as erro:
        console.print(f"[red]Erro ao cadastrar: {erro}[/red]")
