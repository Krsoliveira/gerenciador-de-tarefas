# database.py

import sqlite3
import hashlib
from datetime import date, datetime

def inicializar_banco():
    conn = None
    try:
        conn = sqlite3.connect('gerenciador.db')
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT UNIQUE NOT NULL,
            nome_completo TEXT NOT NULL, username TEXT UNIQUE NOT NULL, 
            password_hash TEXT NOT NULL, nivel_acesso TEXT NOT NULL 
        )''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS casos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL, numero_relatorio TEXT UNIQUE,
            tipo TEXT NOT NULL, data_inicio TEXT NOT NULL, data_final TEXT, status TEXT NOT NULL
        )''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS atividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT, caso_id INTEGER NOT NULL, atividade_desc TEXT,
            testes_realizados TEXT, extensao_exames TEXT, criterio_amostragem TEXT,
            periodo_situacao TEXT, observacao_resumo TEXT, realizado_por TEXT,
            nao_conformidade TEXT, reincidente INTEGER, recomendacao TEXT,
            data_p_solucao TEXT, data_registro TEXT NOT NULL, situacao TEXT,
            FOREIGN KEY (caso_id) REFERENCES casos (id)
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS log_exclusoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, id_caso_excluido INTEGER NOT NULL,
            numero_relatorio_excluido TEXT, titulo_excluido TEXT,
            usuario_codigo TEXT NOT NULL, usuario_nome TEXT NOT NULL, data_exclusao TEXT NOT NULL
        )''')
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao inicializar o banco: {e}")
    finally:
        if conn: conn.close()

def adicionar_usuario(codigo, nome_completo, username, senha, nivel_acesso):
    conn = None
    try:
        conn = sqlite3.connect('gerenciador.db')
        cursor = conn.cursor()
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        cursor.execute('INSERT INTO usuarios (codigo, nome_completo, username, password_hash, nivel_acesso) VALUES (?, ?, ?, ?, ?)', 
                       (codigo, nome_completo, username, senha_hash, nivel_acesso))
        conn.commit()
        return True
    except sqlite3.IntegrityError: return False
    except sqlite3.Error as e: print(f"Ocorreu um erro ao adicionar o usuário: {e}"); return False
    finally:
        if conn: conn.close()

def verificar_login(codigo, senha):
    conn = None
    try:
        conn = sqlite3.connect('gerenciador.db')
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nome_completo, password_hash, nivel_acesso FROM usuarios WHERE codigo = ?", (codigo,))
        usuario_encontrado = cursor.fetchone()
        if usuario_encontrado:
            user_codigo, nome_completo, hash_salvo, nivel = usuario_encontrado
            senha_digitada_hash = hashlib.sha256(senha.encode()).hexdigest()
            if senha_digitada_hash == hash_salvo:
                return (user_codigo, nome_completo, nivel)
        return None
    except sqlite3.Error as e: print(f"Ocorreu um erro durante o login: {e}"); return None
    finally:
        if conn: conn.close()

def deletar_relatorio_e_registrar_log(id_caso, usuario_codigo, usuario_nome):
    conn = None
    try:
        conn = sqlite3.connect('gerenciador.db')
        cursor = conn.cursor()
        cursor.execute("SELECT numero_relatorio, titulo FROM casos WHERE id = ?", (id_caso,))
        dados_caso = cursor.fetchone()
        if not dados_caso: return False
        num_relatorio, titulo = dados_caso
        data_hora_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO log_exclusoes (id_caso_excluido, numero_relatorio_excluido, titulo_excluido, usuario_codigo, usuario_nome, data_exclusao) VALUES (?, ?, ?, ?, ?, ?)",
                       (id_caso, num_relatorio, titulo, usuario_codigo, usuario_nome, data_hora_agora))
        cursor.execute("DELETE FROM atividades WHERE caso_id = ?", (id_caso,))
        cursor.execute("DELETE FROM casos WHERE id = ?", (id_caso,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        if conn: conn.rollback()
        print(f"Ocorreu um erro na exclusão segura: {e}")
        return False
    finally:
        if conn: conn.close()

def buscar_log_exclusoes():
    conn = None
    try:
        conn = sqlite3.connect('gerenciador.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, numero_relatorio_excluido, titulo_excluido, usuario_nome, data_exclusao FROM log_exclusoes ORDER BY id DESC")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao buscar o log: {e}")
        return []
    finally:
        if conn: conn.close()

def buscar_usuarios():
    conn = None
    try: conn = sqlite3.connect('gerenciador.db'); cursor = conn.cursor(); cursor.execute("SELECT codigo, nome_completo FROM usuarios ORDER BY nome_completo"); return cursor.fetchall()
    except sqlite3.Error as e: print(f"Ocorreu um erro ao buscar os usuários: {e}"); return []
    finally:
        if conn: conn.close()

def buscar_casos():
    conn = None
    try: conn = sqlite3.connect('gerenciador.db'); cursor = conn.cursor(); cursor.execute("SELECT id, titulo, data_inicio, data_final, status, numero_relatorio FROM casos ORDER BY data_inicio DESC"); return cursor.fetchall()
    except sqlite3.Error as e: print(f"Ocorreu um erro ao buscar os casos: {e}"); return []
    finally:
        if conn: conn.close()

def buscar_ultimo_numero_relatorio_do_ano(ano):
    conn = None
    try: conn = sqlite3.connect('gerenciador.db'); cursor = conn.cursor(); cursor.execute("SELECT numero_relatorio FROM casos WHERE numero_relatorio LIKE ? ORDER BY numero_relatorio DESC LIMIT 1", (f"{ano}.%",)); resultado = cursor.fetchone(); return int(resultado[0].split('.')[1]) if resultado else 0
    except sqlite3.Error as e: print(f"Erro ao buscar último número do relatório: {e}"); return 0
    finally:
        if conn: conn.close()

def adicionar_novo_caso(titulo, tipo, data_inicio, status):
    conn = None
    try: conn = sqlite3.connect('gerenciador.db'); cursor = conn.cursor(); ano_atual = date.today().year; ultimo_num = buscar_ultimo_numero_relatorio_do_ano(ano_atual); proximo_num = ultimo_num + 1; numero_relatorio_gerado = f"{ano_atual}.{proximo_num:03d}"; cursor.execute("INSERT INTO casos (titulo, tipo, data_inicio, status, numero_relatorio) VALUES (?, ?, ?, ?, ?)", (titulo, tipo, data_inicio, status, numero_relatorio_gerado)); conn.commit(); return cursor.lastrowid
    except sqlite3.Error as e: print(f"Ocorreu um erro ao adicionar novo caso: {e}"); return None
    finally:
        if conn: conn.close()

def buscar_caso_por_id(id_caso):
    conn = None
    try: conn = sqlite3.connect('gerenciador.db'); conn.row_factory = sqlite3.Row; cursor = conn.cursor(); cursor.execute("SELECT * FROM casos WHERE id = ?", (id_caso,)); resultado = cursor.fetchone(); return dict(resultado) if resultado else None
    except sqlite3.Error as e: print(f"Ocorreu um erro ao buscar o caso por ID: {e}"); return None
    finally:
        if conn: conn.close()

def buscar_atividades_por_caso_id(id_caso):
    conn = None
    try: conn = sqlite3.connect('gerenciador.db'); cursor = conn.cursor(); cursor.execute("SELECT id, atividade_desc, realizado_por, data_registro, situacao FROM atividades WHERE caso_id = ? ORDER BY id", (id_caso,)); return cursor.fetchall()
    except sqlite3.Error as e: print(f"Ocorreu um erro ao buscar as atividades: {e}"); return []
    finally:
        if conn: conn.close()

def salvar_atividade(dados_atividade):
    conn = None
    try: conn = sqlite3.connect('gerenciador.db'); cursor = conn.cursor(); cursor.execute("INSERT INTO atividades (caso_id, atividade_desc, testes_realizados, extensao_exames, criterio_amostragem, periodo_situacao, observacao_resumo, realizado_por, nao_conformidade, reincidente, recomendacao, data_p_solucao, data_registro, situacao) VALUES (:caso_id, :atividade_desc, :testes_realizados, :extensao_exames, :criterio_amostragem, :periodo_situacao, :observacao_resumo, :realizado_por, :nao_conformidade, :reincidente, :recomendacao, :data_p_solucao, :data_registro, :situacao)", dados_atividade); conn.commit(); return True
    except sqlite3.Error as e: print(f"Ocorreu um erro ao salvar a atividade: {e}"); return False
    finally:
        if conn: conn.close()

def buscar_atividade_por_id(id_atividade):
    conn = None
    try: conn = sqlite3.connect('gerenciador.db'); conn.row_factory = sqlite3.Row; cursor = conn.cursor(); cursor.execute("SELECT * FROM atividades WHERE id = ?", (id_atividade,)); atividade = cursor.fetchone(); return dict(atividade) if atividade else None
    except sqlite3.Error as e: print(f"Ocorreu um erro ao buscar a atividade por ID: {e}"); return None
    finally:
        if conn: conn.close()

def atualizar_atividade(id_atividade, dados_atividade):
    conn = None
    try: conn = sqlite3.connect('gerenciador.db'); cursor = conn.cursor(); cursor.execute("UPDATE atividades SET atividade_desc = :atividade_desc, testes_realizados = :testes_realizados, observacao_resumo = :observacao_resumo, extensao_exames = :extensao_exames, criterio_amostragem = :criterio_amostragem, periodo_situacao = :periodo_situacao, situacao = :situacao WHERE id = :id", {**dados_atividade, 'id': id_atividade}); conn.commit(); return True
    except sqlite3.Error as e: print(f"Ocorreu um erro ao atualizar a atividade: {e}"); return False
    finally:
        if conn: conn.close()

def deletar_atividade_por_id(id_atividade):
    conn = None
    try: conn = sqlite3.connect('gerenciador.db'); cursor = conn.cursor(); cursor.execute("DELETE FROM atividades WHERE id = ?", (id_atividade,)); conn.commit(); return True
    except sqlite3.Error as e: print(f"Ocorreu um erro ao deletar a atividade: {e}"); return False
    finally:
        if conn: conn.close()

def adicionar_caso_exemplo():
    conn = sqlite3.connect('gerenciador.db'); cursor = conn.cursor(); cursor.execute("SELECT id FROM casos");
    if cursor.fetchone() is None: adicionar_novo_caso('PRIMEIRO RELATÓRIO DO ANO', 'Auditoria', date.today().strftime("%Y-%m-%d"), 'ABERTO')
    conn.close()

if __name__ == '__main__':
    inicializar_banco()
    adicionar_usuario("28685", "KAIQUE RAFAEL DOS SANTOS OLIVEIRA", "kaique.santos", "senha123", "Junior")
    adicionar_usuario("12345", "MARCOS VINICIUS DAMASCENO", "marcos.vinicius", "outrasenha", "Manager")
    adicionar_caso_exemplo()
    print("Banco de dados inicializado com dados de exemplo e níveis de acesso.")