import os
import sqlite3
import bcrypt

class LoginManager:
    def __init__(self, db_name='users.db'):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_name)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_user_table()

    def _create_user_table(self):
        """Resposavel Por criar a tabela de usuários se ainda não existir."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash BLOB NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'operador'))
            )''')
        self.conn.commit()
    def deletar_usuario(self, username: str) -> bool:
        """Remove um usuário completamente do banco de dados."""
        if not self.user_exists(username):
            return False  # Usuário não existe

        self.cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        self.conn.commit()
        return True
    def register_user(self, username: str, password: str, role: str = 'operador') -> bool:

        """Registra um novo usuário com senha criptografada."""
        if self.user_exists(username):
            return False

        # Gera o hash da senha com bcrypt (Por seguranca somente trabalhamos com o hash da senha e nao a propria senha)
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        if role not in ('admin', 'operador'):
            return False
        # Armazena o usuário e o hash no banco
        self.cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',(username, password_hash, role))
        self.conn.commit()
        return True

    def authenticate_user(self, username: str, password: str) -> bool:
        """Verifica se o usuário e a senha são válidos."""
        self.cursor.execute('SELECT password_hash, role FROM users WHERE username = ?',(username,))
        row = self.cursor.fetchone()
        if row is None:
            
            return False

        stored_hash, role = row
        if bcrypt.checkpw(password.encode(), stored_hash):
            # Autenticação bem-sucedida
            self.conn.close()
            return role
        else:
            # Senha incorreta 
            self.conn.close()
            return False\
            
    def listar_logins(self):
        """Retorna uma lista com todos os usuários e seus respectivos papéis."""
        self.cursor.execute('SELECT username, role FROM users')
        usuarios = self.cursor.fetchall()
        return [{'username': u, 'role': r} for u, r in usuarios]
    
    def user_exists(self, username: str) -> bool:
        """Verifica se um usuário já existe no banco."""
        self.cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
        return self.cursor.fetchone() is not None

    def close(self):
        """Fecha a conexão com o banco de dados."""
        self.conn.close()

if __name__ == '__main__':
    lm = LoginManager()


    lm.register_user('admin', '123','admin')
    lm.register_user('operador', '123','operador')

    if lm.authenticate_user('admin', '123'):
        print("Login bem-sucedido!")
    else:
        print("Credenciais incorretas.")

    lm.close()