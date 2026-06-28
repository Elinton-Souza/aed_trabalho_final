import psycopg2


DB_CONFIG = {
    "host": "ep-cool-dream-ac7hqju8-pooler.sa-east-1.aws.neon.tech",
    "dbname": "neondb",
    "user": "neondb_owner",
    "password": "npg_Rqnu4ATic5jO",
    "port": "5432",
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def ensure_schema():
    sql_mecanicos = """
    CREATE TABLE IF NOT EXISTS mecanicos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL
    )
    """

    sql_manutencoes = """
    CREATE TABLE IF NOT EXISTS manutencoes (
        id SERIAL PRIMARY KEY,
        descricao VARCHAR(150) NOT NULL,
        placa VARCHAR(10) NOT NULL,
        data_servico DATE NOT NULL,
        custo NUMERIC(10, 2) NOT NULL,
        mecanico_id INTEGER NOT NULL,
        FOREIGN KEY (mecanico_id) REFERENCES mecanicos(id) ON DELETE CASCADE
    )
    """

    sql_historico_manutencoes = """
    CREATE TABLE IF NOT EXISTS historico_manutencoes_excluidas (
        id SERIAL PRIMARY KEY,
        manutencao_id INTEGER NOT NULL,
        descricao VARCHAR(150) NOT NULL,
        placa VARCHAR(10) NOT NULL,
        data_servico DATE NOT NULL,
        custo NUMERIC(10, 2) NOT NULL,
        mecanico_id INTEGER NOT NULL,
        mecanico_nome VARCHAR(100),
        excluida_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        motivo VARCHAR(50) NOT NULL DEFAULT 'exclusao'
    )
    """

    sql_historico_manutencoes_alter = """
    ALTER TABLE historico_manutencoes_excluidas
        ADD COLUMN IF NOT EXISTS mecanico_nome VARCHAR(100);

    ALTER TABLE historico_manutencoes_excluidas
        ALTER COLUMN excluida_em TYPE TIMESTAMPTZ USING excluida_em AT TIME ZONE 'America/Sao_Paulo';

    ALTER TABLE historico_manutencoes_excluidas
        ALTER COLUMN excluida_em SET DEFAULT CURRENT_TIMESTAMP;
    """

    sql_funcao_historico = """
    CREATE OR REPLACE FUNCTION registrar_historico_manutencao_excluida()
    RETURNS TRIGGER AS $$
    DECLARE
        v_mecanico_nome VARCHAR(100);
    BEGIN
        SELECT nome
        INTO v_mecanico_nome
        FROM mecanicos
        WHERE id = OLD.mecanico_id;

        IF v_mecanico_nome IS NULL THEN
            RETURN OLD;
        END IF;

        INSERT INTO historico_manutencoes_excluidas (
            manutencao_id,
            descricao,
            placa,
            data_servico,
            custo,
            mecanico_id,
            mecanico_nome,
            excluida_em,
            motivo
        )
        VALUES (
            OLD.id,
            OLD.descricao,
            OLD.placa,
            OLD.data_servico,
            OLD.custo,
            OLD.mecanico_id,
            v_mecanico_nome,
            CURRENT_TIMESTAMP,
            TG_OP
        );

        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """

    sql_funcao_historico_mecanico = """
    CREATE OR REPLACE FUNCTION registrar_historico_mecanico_excluido()
    RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO historico_manutencoes_excluidas (
            manutencao_id,
            descricao,
            placa,
            data_servico,
            custo,
            mecanico_id,
            mecanico_nome,
            excluida_em,
            motivo
        )
        SELECT
            man.id,
            man.descricao,
            man.placa,
            man.data_servico,
            man.custo,
            man.mecanico_id,
            OLD.nome,
            CURRENT_TIMESTAMP,
            TG_OP
        FROM manutencoes man
        WHERE man.mecanico_id = OLD.id;

        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """

    sql_trigger_historico = """
    DROP TRIGGER IF EXISTS trg_registrar_historico_manutencao_excluida ON manutencoes;
    CREATE TRIGGER trg_registrar_historico_manutencao_excluida
    BEFORE DELETE ON manutencoes
    FOR EACH ROW
    EXECUTE FUNCTION registrar_historico_manutencao_excluida();
    """

    sql_trigger_historico_mecanico = """
    DROP TRIGGER IF EXISTS trg_registrar_historico_mecanico_excluido ON mecanicos;
    CREATE TRIGGER trg_registrar_historico_mecanico_excluido
    BEFORE DELETE ON mecanicos
    FOR EACH ROW
    EXECUTE FUNCTION registrar_historico_mecanico_excluido();
    """

    sql_fk_cascade = """
    ALTER TABLE manutencoes
        DROP CONSTRAINT IF EXISTS manutencoes_mecanico_id_fkey;

    ALTER TABLE manutencoes
        ADD CONSTRAINT manutencoes_mecanico_id_fkey
        FOREIGN KEY (mecanico_id) REFERENCES mecanicos(id) ON DELETE CASCADE;
    """

    with get_connection() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(sql_mecanicos)
            cursor.execute(sql_manutencoes)
            cursor.execute(sql_historico_manutencoes)
            cursor.execute(sql_historico_manutencoes_alter)
            cursor.execute(sql_funcao_historico)
            cursor.execute(sql_funcao_historico_mecanico)
            cursor.execute(sql_trigger_historico)
            cursor.execute(sql_trigger_historico_mecanico)
            cursor.execute(sql_fk_cascade)
        conexao.commit()


if __name__ == "__main__":
    ensure_schema()
    print("Tabelas garantidas no banco com sucesso!")
