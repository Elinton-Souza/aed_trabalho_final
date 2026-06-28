# Sistema de Oficina — Boca do Lobo

Trabalho Final da disciplina **Algoritmos e Estruturas de Dados I**
Curso Superior de Tecnologia em Análise e Desenvolvimento de Sistemas — UniSenac Pelotas
Prof. Edécio Fernando Iepsen

Autor: **Elinton Souza Cunha**

---

## Sobre

Aplicação em Python que gerencia mecânicos e manutenções de uma oficina, manipulando um banco PostgreSQL na nuvem (Neon.tech). Atende às 6 funções exigidas pelo Trabalho #3, mais um sistema extra de auditoria automática via *triggers*.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.10+ |
| Banco de dados | PostgreSQL (Neon.tech) |
| Driver | `psycopg2-binary` |
| Interface terminal | `rich` (cores, tabelas, prompts) |
| Gráficos | `plotly` + `pandas` |
| Página web | `flask` (servidor + Jinja2 templates) |

## Modelo de dados

Três tabelas relacionadas:

```
┌──────────────┐        ┌────────────────────┐        ┌────────────────────────────────┐
│  mecanicos   │ 1───N  │   manutencoes      │ ──→    │ historico_manutencoes_excluidas│
│  (auxiliar)  │        │   (principal)      │ trigger│ (auditoria — preenchida        │
│              │        │                    │        │  automaticamente em DELETE)    │
│  id          │◄───────┤  mecanico_id  FK   │        │                                │
│  nome        │ ON DEL │  descricao         │        │  (espelha a manutenção         │
│              │ CASCADE│  placa             │        │   excluída + nome do mecânico  │
│              │        │  data_servico      │        │   + data/hora + motivo)        │
│              │        │  custo             │        │                                │
└──────────────┘        └────────────────────┘        └────────────────────────────────┘
```

**Relacionamento:** cada manutenção pertence a **um** mecânico (`FOREIGN KEY mecanico_id`). Se um mecânico for excluído, suas manutenções são apagadas em cascata (`ON DELETE CASCADE`).

**Auditoria automática (extra):** duas funções *PL/pgSQL* + dois *triggers* `BEFORE DELETE` garantem que toda exclusão (manual ou cascateada) seja registrada em `historico_manutencoes_excluidas`.

## Estrutura de arquivos

```
aed_trabalho_final/
├── db.py                   # Conexão + criação das 3 tabelas + funções e triggers PL/pgSQL
├── main.py                 # Menu principal (loop while + Prompt.ask)
├── web.py                  # Servidor Flask (página web — Função 5)
├── requirements.txt        # Dependências do projeto
├── .gitignore
├── esporte-clube-pelotas-logo-png_seeklogo-321252.png   # Logo direita
├── images.jpg              # Logo esquerda
└── operacoes/
    ├── pesquisa.py         # Pesquisa avançada (Função 3)
    ├── grafico.py          # Gráficos Plotly com agrupamento (Função 4)
    ├── backup.py           # Backup CSV/JSON (Função 6)
    ├── web_runner.py       # Helper: inicia web.py em subprocesso e abre o navegador
    ├── mecanicos/          # CRUD da tabela auxiliar (Função 1)
    │   ├── incluir.py
    │   ├── listar.py
    │   ├── alterar.py
    │   └── excluir.py
    └── manutencoes/        # CRUD da tabela principal (Função 2)
        ├── incluir.py
        ├── listar.py
        ├── alterar.py
        ├── excluir.py
        └── historico.py    # Lista o histórico de exclusões
```

## Como rodar

### Pré-requisitos
- Python 3.10 ou superior
- Acesso à internet (banco Neon.tech está na nuvem)

### Instalação
```bash
pip install -r requirements.txt
```

### Execução
```bash
python main.py
```

O menu principal abre. O esquema do banco (tabelas + triggers) é criado/garantido na primeira execução.

## Menu — mapeamento das funções do trabalho

| Opção do menu | Função do trabalho | Arquivos envolvidos |
|---------------|--------------------|-----------------------|
| **1. Mecânicos (CRUD — tabela auxiliar)** | Função 1 | `operacoes/mecanicos/*.py` |
| **2. Manutenções (CRUD — tabela principal)** | Função 2 | `operacoes/manutencoes/*.py` |
| **3. Pesquisa avançada** | Função 3 | `operacoes/pesquisa.py` |
| **4. Gerar gráfico** | Função 4 | `operacoes/grafico.py` |
| **5. Iniciar página web** | Função 5 | `web.py` + `operacoes/web_runner.py` |
| **6. Backup (CSV/JSON)** | Função 6 | `operacoes/backup.py` |

## Padrões arquiteturais

### Centralização da conexão (`db.py`)
Antes, cada arquivo abria sua própria conexão repetindo as credenciais. Isso é ruim porque qualquer mudança na senha exige editar muitos arquivos, e código duplicado convida bugs. A solução foi centralizar a conexão em `db.py` e fazer todos os outros arquivos importarem `get_connection()` daqui.

### Context manager (`with`)
Todo bloco que abre conexão usa `with get_connection() as conexao:` e dentro `with conexao.cursor() as cursor:`. Isso garante que conexões e cursores sejam fechados automaticamente, mesmo se ocorrer erro no meio. É o equivalente do `try/finally` manual, mais limpo.

### Try/except
Toda função que toca no banco envolve a operação em `try/except`. Se o banco cair ou der erro de SQL, o programa não quebra — mostra uma mensagem amigável e volta para o menu.

### Parâmetros seguros (`%s`)
Valores nunca são concatenados em string SQL — vão sempre como parâmetros separados via `cursor.execute(sql, tupla)`. Isso evita SQL Injection e trata tipos automaticamente.

### Padrão "buscar antes de mutar"
Antes de `UPDATE` ou `DELETE`, fazemos um `SELECT` para confirmar que o registro existe. Vantagens: mensagens claras quando o ID não existe, valores atuais podem virar `default` no `Prompt.ask`, e operações destrutivas podem ser confirmadas com `Confirm.ask`.

### `RealDictCursor`
Quando precisamos acessar colunas pelo nome (`mecanico["nome"]`), usamos `cursor_factory=RealDictCursor`. Isso transforma cada linha de tupla `(1, "Edécio")` em dicionário `{"id": 1, "nome": "Edécio"}`. Mais legível e à prova de mudanças na ordem das colunas.

## Sistema de auditoria (diferencial)

A tabela `historico_manutencoes_excluidas` é preenchida **automaticamente** por dois *triggers* `BEFORE DELETE` que disparam funções PL/pgSQL (código que roda dentro do PostgreSQL, não no Python):

- `registrar_historico_manutencao_excluida` — dispara quando uma manutenção é deletada diretamente.
- `registrar_historico_mecanico_excluido` — dispara antes de um mecânico ser deletado: copia todas as manutenções dele para o histórico, *antes* do cascade as apagar.

Resultado: o usuário do sistema não precisa lembrar de logar nada. O banco faz isso sozinho, independente do caminho da exclusão.

## Arquivos auxiliares gerados pelo programa

Pastas criadas automaticamente quando você usa as funções correspondentes (já estão no `.gitignore`):

- `backups/` — arquivos `.csv` e `.json` gerados pela Função 6
- `graficos/` — arquivos `.html` gerados pela Função 4

## Visual da página web

Cabeçalho com cores do EC Pelotas (azul royal `#1958A8` + amarelo `#F8C30A`):
- Logo esquerda (imagem do projeto)
- Título "Oficina Boca do Lobo" + subtítulo "PAINEL DE MANUTENÇÕES" centralizados
- Logo direita (escudo do EC Pelotas)
- Borda inferior amarela separando do conteúdo

Conteúdo principal:
- Dropdown para filtrar por mecânico (ou ver todos)
- Resumo do filtro atual (quantidade + total)
- 3 cards com as mesmas informações dos gráficos (custo por mecânico, quantidade por mecânico, top 10 placas)
- Tabela detalhada de todas as manutenções

## Conceitos demonstrados (defesa do trabalho)

- Estruturas de dados Python: listas, tuplas, dicionários, listas de dicionários
- CRUD completo em banco relacional
- JOIN entre tabelas
- Agregações (`GROUP BY`, `SUM`, `COUNT`, `ORDER BY`)
- Cláusulas `WHERE` dinâmicas (pesquisa avançada)
- Foreign Keys e `ON DELETE CASCADE`
- Triggers e funções PL/pgSQL
- Serialização (CSV, JSON, conversão de `Decimal` e `date`)
- Servidor HTTP simples com Flask + Jinja2
- Templates com filtros e fluxo condicional
- Visualização de dados com Plotly e Pandas
