from psycopg2.extras import RealDictCursor
from rich.console import Console
from rich.table import Table
from zoneinfo import ZoneInfo

from db import get_connection

console = Console()
fuso_brasilia = ZoneInfo("America/Sao_Paulo")


def listar_historico_manutencoes_excluidas():
    try:
        with get_connection() as conexao:
            with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        manutencao_id,
                        descricao,
                        placa,
                        data_servico,
                        custo,
                        mecanico_id,
                        COALESCE(mecanico_nome, 'Mecânico removido') AS mecanico_nome,
                        excluida_em,
                        motivo
                    FROM historico_manutencoes_excluidas
                    ORDER BY excluida_em DESC, id DESC
                    """
                )
                historico = cursor.fetchall()
    except Exception as erro:
        console.print(f"[red]Erro ao buscar histórico: {erro}[/red]")
        return

    if not historico:
        console.print("[yellow]Nenhuma exclusão registrada no histórico.[/yellow]")
        return

    tabela = Table(title="Histórico de manutenções excluídas")
    tabela.add_column("ID Hist.", justify="right", style="cyan")
    tabela.add_column("ID Manut.", justify="right", style="white")
    tabela.add_column("Descrição", style="white")
    tabela.add_column("Placa", style="yellow")
    tabela.add_column("Data", style="green")
    tabela.add_column("Custo", justify="right", style="magenta")
    tabela.add_column("Mecânico", style="blue")
    tabela.add_column("Excluída em", style="bright_black")
    tabela.add_column("Motivo", style="red")

    for item in historico:
        excluida_em = item["excluida_em"]
        if excluida_em.tzinfo is not None:
            excluida_em = excluida_em.astimezone(fuso_brasilia)
        tabela.add_row(
            str(item["id"]),
            str(item["manutencao_id"]),
            item["descricao"],
            item["placa"],
            item["data_servico"].strftime("%d/%m/%Y"),
            f"R$ {item['custo']:>9.2f}",
            f"{item['mecanico_nome']} (ID {item['mecanico_id']})",
            excluida_em.strftime("%d/%m/%Y %H:%M:%S"),
            item["motivo"],
        )

    console.print(tabela)
