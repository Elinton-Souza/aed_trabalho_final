import subprocess
import sys
import time
import webbrowser

from rich.console import Console

console = Console()


def iniciar_web():
    console.print("\n[bold blue]Servidor Web — Manutenções[/bold blue]")
    console.print("[dim]Iniciando Flask em http://localhost:5000 ...[/dim]")
    console.print("[yellow]Para parar o servidor, pressione Ctrl+C nesta janela.[/yellow]\n")

    processo = subprocess.Popen([sys.executable, "web.py"])

    time.sleep(1.5)
    webbrowser.open("http://localhost:5000")

    try:
        processo.wait()
    except KeyboardInterrupt:
        console.print("\n[cyan]Encerrando servidor...[/cyan]")
        processo.terminate()
        processo.wait()
