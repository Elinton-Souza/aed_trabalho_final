from flask import Flask, render_template_string, request, send_from_directory
from psycopg2.extras import RealDictCursor

from db import get_connection


app = Flask(__name__)

ARQUIVO_LOGO_DIR = "esporte-clube-pelotas-logo-png_seeklogo-321252.png"
ARQUIVO_LOGO_ESQ = "images.jpg"


PAGINA = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Oficina Boca do Lobo</title>
    <style>
        :root {
            --azul: #1958A8;
            --azul-escuro: #0F3B7A;
            --amarelo: #F8C30A;
            --amarelo-claro: #FFF4D0;
            --creme: #FFFEF7;
            --texto: #1a2942;
            --cinza: #e8e8e8;
        }

        body { font-family: Arial, sans-serif; margin: 0; padding: 0;
               background: var(--creme); color: var(--texto); }

        header {
            background: linear-gradient(135deg, var(--azul) 0%, var(--azul-escuro) 100%);
            color: white;
            padding: 24px 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 5px solid var(--amarelo);
        }
        .header-logo-esq, .header-logo-dir { width: 110px; flex-shrink: 0; }
        .header-logo-esq img, .header-logo-dir img {
            height: 110px; width: 110px; object-fit: contain;
            background: white; border-radius: 50%; padding: 4px;
        }
        .titulo-area { flex: 1; text-align: center; }
        .titulo-area h1 {
            margin: 0;
            font-size: 2.2em;
            letter-spacing: 1px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .titulo-area .subtitulo {
            margin: 6px 0 0 0;
            font-size: 1.05em;
            font-weight: 300;
            color: var(--amarelo);
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        main { padding: 30px 40px; }

        .filtro {
            background: white; padding: 16px 20px; border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08); margin-bottom: 24px;
            display: flex; gap: 12px; align-items: center;
            border-top: 3px solid var(--amarelo);
        }
        .filtro label { font-weight: bold; color: var(--azul); }
        .filtro select {
            padding: 8px 12px; border: 1px solid #ccc;
            border-radius: 4px; font-size: 1em; min-width: 240px;
        }
        .filtro select:focus { outline: 2px solid var(--amarelo); border-color: var(--azul); }
        .filtro button {
            padding: 8px 16px; background: var(--azul); color: white;
            border: none; border-radius: 4px; cursor: pointer;
        }

        .resumo {
            background: var(--amarelo-claro); padding: 12px 20px; border-radius: 8px;
            margin-bottom: 24px; border-left: 4px solid var(--azul);
        }
        .resumo strong { color: var(--azul-escuro); }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 20px; margin-bottom: 30px;
        }
        .card {
            background: white; border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08); overflow: hidden;
            border-top: 3px solid var(--amarelo);
        }
        .card h3 {
            margin: 0; padding: 14px 18px;
            background: var(--azul); color: white; font-size: 1em;
        }
        .card table { width: 100%; border-collapse: collapse; }
        .card th, .card td { padding: 10px 14px; text-align: left;
                             border-bottom: 1px solid #eee; }
        .card th { background: #f7f9fc; font-weight: 600; color: var(--azul-escuro); }
        .card .num { text-align: right; font-variant-numeric: tabular-nums; }
        .card tr:last-child td { border-bottom: none; }
        .card tr:hover td { background: var(--amarelo-claro); }
        .vazio { padding: 20px; color: #888; text-align: center; }

        h2 { color: var(--azul); margin-top: 30px; }
        .lista {
            background: white; border-radius: 8px; overflow: hidden;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            border-top: 3px solid var(--amarelo);
        }
        .lista table { width: 100%; border-collapse: collapse; }
        .lista th, .lista td { padding: 12px; text-align: left;
                                border-bottom: 1px solid #eee; }
        .lista th { background: var(--azul); color: white; }
        .lista tr:hover { background: var(--amarelo-claro); }
        .lista .custo {
            text-align: right; font-weight: bold;
            color: var(--azul-escuro);
            font-variant-numeric: tabular-nums;
        }
        .total {
            margin-top: 16px; font-size: 1.2em; text-align: right;
            padding-right: 12px;
        }
        .total strong { color: var(--azul); }
    </style>
</head>
<body>
    <header>
        <div class="header-logo-esq">
            <img src="/logo-esq" alt="Logo esquerda">
        </div>

        <div class="titulo-area">
            <h1>Oficina Boca do Lobo</h1>
            <p class="subtitulo">Painel de Manutenções</p>
        </div>

        <div class="header-logo-dir">
            <img src="/logo-dir" alt="EC Pelotas">
        </div>
    </header>

    <main>
        <form class="filtro" method="get" action="/">
            <label for="mecanico_id">Filtrar por mecânico:</label>
            <select name="mecanico_id" id="mecanico_id" onchange="this.form.submit()">
                <option value="">— Todos os mecânicos —</option>
                {% for m in mecanicos %}
                <option value="{{ m.id }}" {% if filtro_id == m.id|string %}selected{% endif %}>
                    {{ m.nome }}
                </option>
                {% endfor %}
            </select>
            <noscript><button type="submit">Filtrar</button></noscript>
        </form>

        <div class="resumo">
            Exibindo dados de: <strong>{{ nome_filtro }}</strong>
            &nbsp;|&nbsp; {{ manutencoes|length }} manutenção(ões)
            &nbsp;|&nbsp; total R$ {{ '%.2f'|format(total_geral) }}
        </div>

        <div class="grid">
            <div class="card">
                <h3>💰 Custo total por mecânico</h3>
                {% if custos_por_mec %}
                <table>
                    <thead><tr><th>Mecânico</th><th class="num">Custo total</th></tr></thead>
                    <tbody>
                    {% for c in custos_por_mec %}
                        <tr>
                            <td>{{ c.mecanico }}</td>
                            <td class="num">R$ {{ '%.2f'|format(c.total) }}</td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
                {% else %}<p class="vazio">Sem dados.</p>{% endif %}
            </div>

            <div class="card">
                <h3>🔢 Quantidade de serviços por mecânico</h3>
                {% if qtd_por_mec %}
                <table>
                    <thead><tr><th>Mecânico</th><th class="num">Qtd</th></tr></thead>
                    <tbody>
                    {% for q in qtd_por_mec %}
                        <tr>
                            <td>{{ q.mecanico }}</td>
                            <td class="num">{{ q.quantidade }}</td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
                {% else %}<p class="vazio">Sem dados.</p>{% endif %}
            </div>

            <div class="card">
                <h3>🚗 Top 10 placas (custo acumulado)</h3>
                {% if top_placas %}
                <table>
                    <thead><tr><th>Placa</th><th class="num">Serviços</th><th class="num">Total</th></tr></thead>
                    <tbody>
                    {% for p in top_placas %}
                        <tr>
                            <td>{{ p.placa }}</td>
                            <td class="num">{{ p.qtd }}</td>
                            <td class="num">R$ {{ '%.2f'|format(p.total) }}</td>
                        </tr>
                    {% endfor %}
                    </tbody>
                </table>
                {% else %}<p class="vazio">Sem dados.</p>{% endif %}
            </div>
        </div>

        <h2>📋 Manutenções detalhadas</h2>
        <div class="lista">
            {% if manutencoes %}
            <table>
                <thead>
                    <tr>
                        <th>ID</th><th>Descrição</th><th>Placa</th>
                        <th>Data</th><th>Custo</th><th>Mecânico</th>
                    </tr>
                </thead>
                <tbody>
                    {% for m in manutencoes %}
                    <tr>
                        <td>{{ m.id }}</td>
                        <td>{{ m.descricao }}</td>
                        <td>{{ m.placa }}</td>
                        <td>{{ m.data_servico.strftime('%d/%m/%Y') }}</td>
                        <td class="custo">R$ {{ '%.2f'|format(m.custo) }}</td>
                        <td>{{ m.mecanico }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="vazio">Nenhuma manutenção encontrada para este filtro.</p>
            {% endif %}
            <p class="total">Total: <strong>R$ {{ '%.2f'|format(total_geral) }}</strong></p>
        </div>
    </main>
</body>
</html>
"""


@app.route("/logo-dir")
def logo_direita():
    return send_from_directory(".", ARQUIVO_LOGO_DIR)


@app.route("/logo-esq")
def logo_esquerda():
    return send_from_directory(".", ARQUIVO_LOGO_ESQ)


@app.route("/")
def index():
    mecanico_id_txt = request.args.get("mecanico_id", "").strip()
    mecanico_id_int = int(mecanico_id_txt) if mecanico_id_txt.isdigit() else None

    filtro_wh = ""
    params = ()
    if mecanico_id_int is not None:
        filtro_wh = "AND mec.id = %s"
        params = (mecanico_id_int,)

    with get_connection() as conexao:
        with conexao.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute("SELECT id, nome FROM mecanicos ORDER BY nome")
            mecanicos = cursor.fetchall()

            nome_filtro = "Todos os mecânicos"
            if mecanico_id_int is not None:
                for m in mecanicos:
                    if m["id"] == mecanico_id_int:
                        nome_filtro = m["nome"]
                        break

            cursor.execute(f"""
                SELECT mec.nome AS mecanico, SUM(man.custo) AS total
                FROM manutencoes man
                JOIN mecanicos mec ON mec.id = man.mecanico_id
                WHERE 1=1 {filtro_wh}
                GROUP BY mec.nome
                ORDER BY total DESC
            """, params)
            custos_por_mec = cursor.fetchall()

            cursor.execute(f"""
                SELECT mec.nome AS mecanico, COUNT(*) AS quantidade
                FROM manutencoes man
                JOIN mecanicos mec ON mec.id = man.mecanico_id
                WHERE 1=1 {filtro_wh}
                GROUP BY mec.nome
                ORDER BY quantidade DESC
            """, params)
            qtd_por_mec = cursor.fetchall()

            cursor.execute(f"""
                SELECT man.placa, COUNT(*) AS qtd, SUM(man.custo) AS total
                FROM manutencoes man
                JOIN mecanicos mec ON mec.id = man.mecanico_id
                WHERE 1=1 {filtro_wh}
                GROUP BY man.placa
                ORDER BY total DESC
                LIMIT 10
            """, params)
            top_placas = cursor.fetchall()

            cursor.execute(f"""
                SELECT man.id, man.descricao, man.placa, man.data_servico,
                       man.custo, mec.nome AS mecanico
                FROM manutencoes man
                JOIN mecanicos mec ON mec.id = man.mecanico_id
                WHERE 1=1 {filtro_wh}
                ORDER BY man.data_servico DESC
            """, params)
            manutencoes = cursor.fetchall()

    total_geral = sum(float(m["custo"]) for m in manutencoes)

    return render_template_string(
        PAGINA,
        mecanicos=mecanicos,
        filtro_id=mecanico_id_txt,
        nome_filtro=nome_filtro,
        custos_por_mec=custos_por_mec,
        qtd_por_mec=qtd_por_mec,
        top_placas=top_placas,
        manutencoes=manutencoes,
        total_geral=total_geral,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
