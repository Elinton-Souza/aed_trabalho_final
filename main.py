from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from db import ensure_schema

from operacoes.mecanicos.incluir import incluir_mecanico
from operacoes.mecanicos.listar import listar_mecanicos
from operacoes.mecanicos.alterar import alterar_mecanico
from operacoes.mecanicos.excluir import excluir_mecanico

from operacoes.manutencoes.incluir import incluir_manutencao
from operacoes.manutencoes.listar import listar_manutencoes
from operacoes.manutencoes.alterar import alterar_manutencao
from operacoes.manutencoes.excluir import excluir_manutencao
from operacoes.manutencoes.historico import listar_historico_manutencoes_excluidas

from operacoes.pesquisa import pesquisa_avancada
from operacoes.grafico import gerar_grafico
from operacoes.backup import gerar_backup
from operacoes.web_runner import iniciar_web

console = Console()


def menu_mecanicos():
    while True:
        console.print(Panel.fit(
            "1. Incluir mecânico\n"
            "2. Listar mecânicos\n"
            "3. Alterar mecânico\n"
            "4. Excluir mecânico\n"
            "0. Voltar",
            title="[bold cyan]Mecânicos[/bold cyan]"
        ))
        opcao = Prompt.ask("Escolha", choices=["0", "1", "2", "3", "4"], default="0")

        if opcao == "1":
            incluir_mecanico()
        elif opcao == "2":
            listar_mecanicos()
        elif opcao == "3":
            alterar_mecanico()
        elif opcao == "4":
            excluir_mecanico()
        else:
            break


def menu_manutencoes():
    while True:
        console.print(Panel.fit(
            "1. Incluir manutenção\n"
            "2. Listar manutenções\n"
            "3. Alterar manutenção\n"
            "4. Excluir manutenção\n"
            "5. Histórico de exclusões\n"
            "0. Voltar",
            title="[bold cyan]Manutenções[/bold cyan]"
        ))
        opcao = Prompt.ask("Escolha", choices=["0", "1", "2", "3", "4", "5"], default="0")

        if opcao == "1":
            incluir_manutencao()
        elif opcao == "2":
            listar_manutencoes()
        elif opcao == "3":
            alterar_manutencao()
        elif opcao == "4":
            excluir_manutencao()
        elif opcao == "5":
            listar_historico_manutencoes_excluidas()
        else:
            break


def menu_principal():
    while True:
        console.print(Panel.fit(
            "1. Mecânicos (CRUD — tabela auxiliar)\n"
            "2. Manutenções (CRUD — tabela principal)\n"
            "3. Pesquisa avançada\n"
            "4. Gerar gráfico\n"
            "5. Iniciar página web\n"
            "6. Backup (CSV/JSON)\n"
            "0. Sair",
            title="[bold green]Oficina Boca do Lobo — Trabalho #3[/bold green]",
            subtitle="[bold green]Elinton Souza Cunha[/bold green]"
        ))
        opcao = Prompt.ask("Escolha", choices=["0", "1", "2", "3", "4", "5", "6"], default="0")

        if opcao == "1":
            menu_mecanicos()
        elif opcao == "2":
            menu_manutencoes()
        elif opcao == "3":
            pesquisa_avancada()
        elif opcao == "4":
            gerar_grafico()
        elif opcao == "5":
            iniciar_web()
        elif opcao == "6":
            gerar_backup()
        else:
            console.print("[bold cyan]Até a próxima![/bold cyan]")
            break


if __name__ == "__main__":
    ensure_schema()
    menu_principal()
