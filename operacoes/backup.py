import csv
import json
import os
from datetime import datetime, date
from decimal import Decimal

from psycopg2.extras import RealDictCursor
from rich.console import Console
from rich.prompt import Prompt

from db import get_connection

console = Console()

PASTA_BACKUP = "backups"


def _buscar_manutencoes():
    with get_connection() as conexao:
        with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT man.id, man.descricao, man.placa, man.data_servico,
                       man.custo, mec.nome AS mecanico
                FROM manutencoes man
                JOIN mecanicos mec ON mec.id = man.mecanico_id
                ORDER BY man.id
            """)
            return cursor.fetchall()


def _buscar_historico_manutencoes():
    with get_connection() as conexao:
        with conexao.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
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
            """)
            return cursor.fetchall()


def _converter_para_json(valor):
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()
    raise TypeError(f"Tipo não serializável: {type(valor)}")


def gerar_backup():
    console.print("\n[bold cyan]Backup[/bold cyan]")

    console.print("\n[cyan]Quais dados você quer salvar?[/cyan]")
    console.print("  1. Manutenções (tabela principal — registros ativos)")
    console.print("  2. Histórico de exclusões (auditoria — registros apagados)")
    opcao_origem = Prompt.ask("Escolha", choices=["1", "2"], default="1")
    origem = "manutencoes" if opcao_origem == "1" else "historico"

    console.print("\n[cyan]Qual formato do arquivo?[/cyan]")
    console.print("  1. CSV (abre direto no Excel)")
    console.print("  2. JSON (formato para integração com outros sistemas)")
    opcao_formato = Prompt.ask("Escolha", choices=["1", "2"], default="1")
    formato = "csv" if opcao_formato == "1" else "json"

    try:
        if origem == "historico":
            registros = _buscar_historico_manutencoes()
        else:
            registros = _buscar_manutencoes()
    except Exception as erro:
        console.print(f"[red]Erro ao buscar dados: {erro}[/red]")
        return

    if not registros:
        if origem == "historico":
            console.print("[yellow]Sem histórico de exclusões para fazer backup.[/yellow]")
        else:
            console.print("[yellow]Sem manutenções para fazer backup.[/yellow]")
        return

    os.makedirs(PASTA_BACKUP, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefixo = "historico_manutencoes" if origem == "historico" else "manutencoes"
    nome_arquivo = os.path.join(PASTA_BACKUP, f"{prefixo}_{timestamp}.{formato}")

    try:
        if formato == "csv":
            with open(nome_arquivo, mode="w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=registros[0].keys())
                escritor.writeheader()
                for m in registros:
                    linha = {
                        chave: (valor.isoformat() if isinstance(valor, (datetime, date))
                                else float(valor) if isinstance(valor, Decimal)
                                else valor)
                        for chave, valor in m.items()
                    }
                    escritor.writerow(linha)
        else:
            with open(nome_arquivo, mode="w", encoding="utf-8") as arquivo:
                json.dump(
                    registros,
                    arquivo,
                    indent=2,
                    ensure_ascii=False,
                    default=_converter_para_json
                )

        console.print(
            f"[green]Backup gerado:[/green] [bold]{nome_arquivo}[/bold] "
            f"({len(registros)} registro(s))"
        )
    except Exception as erro:
        console.print(f"[red]Erro ao gravar arquivo: {erro}[/red]")
