import hashlib
import os
import json

from cryptography.fernet import Fernet

class CriptografiaDados:
    def __init__(self, key_path='secret.key'):
        self.key_path = key_path
        self.fernet = self._load_or_create_key()

    def _load_or_create_key(self):
        if not os.path.exists(self.key_path):
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as f:
                f.write(key)
        else:
            with open(self.key_path, 'rb') as f:
                key = f.read()
        return Fernet(key)

    def criptografar(self, valor):
        if valor is None or valor == '':
            return ''
        
        if isinstance(valor, int):
            tipo_valor = 'int'
        elif isinstance(valor, float):
            tipo_valor = 'float'
        else:
            tipo_valor = 'str'
        
        valor_com_tipo = json.dumps({
            'tipo': tipo_valor,
            'valor': str(valor)
        })

        return self.fernet.encrypt(valor_com_tipo.encode()).decode()

    def descriptografar(self, valor_criptografado):
        if not valor_criptografado:
            return ''

        try:
            texto = self.fernet.decrypt(valor_criptografado.encode()).decode()
            dados = json.loads(texto)

            tipo = dados.get('tipo')
            valor = dados.get('valor')

            if tipo == 'int':
                return int(valor)
            elif tipo == 'float':
                return float(valor)
            else:
                return valor

        except Exception as e:
            return f'[ERRO-CRIPTO]'
        
    @staticmethod
    def gerar_hash(email: str) -> str:
        return hashlib.sha256(email.encode()).hexdigest()


if __name__ == '__main__':
    pass