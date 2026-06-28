from datetime import datetime

from psycopg2.extras import RealDictCursor
from rich.console import Console
from rich.prompt import Prompt

from db import get_connection

console = Console()


def alterar_manutencao():
    console.print("\n[bold yellow]Alteração de Manutenção[/bold yellow]")

    id_manutencao = Prompt.ask("ID da manutenção que deseja alterar")

    try:
        with get_connection() as conexao:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT id, descricao, placa, data_servico, custo, mecanico_id "
                    "FROM manutencoes WHERE id = %s",
                    (id_manutencao,)
                )
                m = cursor.fetchone()

            if m is None:
                console.print("[red]Manutenção não encontrada.[/red]")
                return

            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT id, nome FROM mecanicos ORDER BY nome")
                mecanicos = cursor.fetchall()

            descricao = Prompt.ask("Descrição", default=m["descricao"]).strip()
            placa = Prompt.ask("Placa", default=m["placa"]).strip().upper()

            data_texto = Prompt.ask(
                "Data (AAAA-MM-DD)",
                default=m["data_servico"].isoformat()
            )
            try:
                data_servico = datetime.strptime(data_texto, "%Y-%m-%d").date()
            except ValueError:
                console.print("[red]Data inválida.[/red]")
                return

            custo_texto = Prompt.ask("Custo (R$)", default=f"{m['custo']:.2f}")
            try:
                custo = float(custo_texto)
            except ValueError:
                console.print("[red]Custo inválido.[/red]")
                return

            console.print("\n[cyan]Mecânicos disponíveis:[/cyan]")
            for mec in mecanicos:
                console.print(f"  [bold]{mec['id']:>2}[/bold] - {mec['nome']}")

            ids_validos = [str(mec["id"]) for mec in mecanicos]
            mecanico_id = Prompt.ask(
                "ID do mecânico",
                choices=ids_validos,
                default=str(m["mecanico_id"])
            )

            with conexao.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE manutencoes
                    SET descricao = %s, placa = %s, data_servico = %s,
                        custo = %s, mecanico_id = %s
                    WHERE id = %s
                    """,
                    (descricao, placa, data_servico, custo, int(mecanico_id), id_manutencao)
                )
            conexao.commit()

        console.print("[green]Manutenção atualizada com sucesso.[/green]")
    except Exception as erro:
        console.print(f"[red]Erro ao alterar: {erro}[/red]")
