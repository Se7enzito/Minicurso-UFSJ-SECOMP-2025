import sqlite3 as sql
import os

from libs.encrypt import CriptografiaDados

encrypt = CriptografiaDados()

class Conexao():
    def __init__(self) -> None:
        self.database = self.database = os.path.join("backend", "libs", "db", "database.db")
        self.connection = None
        self.cursor = None
    
    def conectar(self) -> None:
        self.connection = sql.connect(self.database, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def desconectar(self) -> None:
        self.connection.close()
        
    def criarTabelas(self) -> None:
        self.conectar()
        # Users
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            user_hash TEXT NOT NULL,
            email TEXT NOT NULL,
            email_hash TEXT NOT NULL,
            password TEXT NOT NULL,
            termos_aceito TEXT DEFAULT 'Eu aceitos todos os termos de uso'
            );""")
        
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        
        self.connection.commit()
        self.desconectar()
    
    # Users
    def listarUsers(self) -> list:
        self.conectar()
        
        users = self.cursor.execute("SELECT user FROM users;").fetchall()
        nomes = [encrypt.descriptografar(user[0]) for user in users]
        
        self.desconectar()
        
        return nomes
        
    def listarEmails(self) -> list:
        self.conectar()
        
        emailsCript = self.cursor.execute("SELECT email FROM users;").fetchall()
        emails = [encrypt.descriptografar(email[0]) for email in emailsCript]
                        
        self.desconectar()
            
        return emails

    def criarUser(self, user: str, email: str, senha: str) -> str:
        users = self.listarUsers()
        emails = self.listarEmails()
        
        self.conectar()
        
        if user in users:
            return "Nome de utilizador já existe."
        
        elif email in emails:
            return "Email já existe."
        
        else:
            userCript = encrypt.criptografar(user)
            emailCript = encrypt.criptografar(email)
            senhaCript = encrypt.criptografar(senha)
            
            userHash = encrypt.gerar_hash(user)
            emailHash = encrypt.gerar_hash(email)
            
            self.cursor.execute("INSERT INTO users (user, user_hash, email, email_hash, password) VALUES (?, ?, ?, ?, ?);", (userCript, userHash, emailCript, emailHash, senhaCript))
            
            self.connection.commit()
            self.desconectar()
            
            return "Utilizador criado com sucesso."
        
    def getId(self, email: str) -> int:
        self.conectar()
        
        emailHash = encrypt.gerar_hash(email)
        result = self.cursor.execute("SELECT id FROM users WHERE email_hash = ?;", (emailHash,)).fetchone()
        
        self.desconectar()
        
        if result is None:
            return -1
        
        return result[0]
    
    def getUser(self, id: int) -> str:
        self.conectar()
        
        user = self.cursor.execute("SELECT user FROM users WHERE id = ?;", (id,)).fetchone()
        
        self.desconectar()
        
        if user is None:
            return 'Id não encontrado'
    
        return encrypt.descriptografar(user[0])
    
    def getUserInfos(self, id: int) -> list:
        self.conectar()
        
        user = self.cursor.execute("SELECT * FROM users WHERE id = ?;", (id,)).fetchone()
        
        self.desconectar()
        
        if user is None:
            return 'Id não encontrado'
        
        userInfosDecrypt = [
            user[0],
            encrypt.descriptografar(user[1]),
            user[2],
            encrypt.descriptografar(user[3]),
            user[4],
            encrypt.descriptografar(user[5]),
            user[6]
        ]
        
        return userInfosDecrypt
            
    def confirmLogin(self, email: str, password: str) -> bool:
        self.conectar()
        
        if email not in self.listarEmails():
            return False
        
        id = self.getId(email)
        if id == -1:
            return False
        
        senha = self.cursor.execute("SELECT password FROM users WHERE id=?;", (id,)).fetchone()
        
        self.desconectar()
        
        if senha is None:
            return False
        
        senhaDecrypt = encrypt.descriptografar(senha[0])
        
        if senhaDecrypt == password:
            return True
        else:
            return False

    def getDadosDecrypt(self) -> list:
        self.conectar()
        
        dados = self.cursor.execute("SELECT * FROM users;").fetchall()
        
        self.desconectar()
        
        if dados is None:
            return []
        
        dadosList = []
        
        for user in dados:
            userInfosDecrypt = [
                user[0],
                encrypt.descriptografar(user[1]),
                user[2],
                encrypt.descriptografar(user[3]),
                user[4],
                encrypt.descriptografar(user[5]),
                user[6]
            ]
            dadosList.append(userInfosDecrypt)
        
        return dadosList

if __name__ == "__main__":
    pass