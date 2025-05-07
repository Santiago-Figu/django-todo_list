import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
from dotenv import load_dotenv

class AESCipher:
    def __init__(self, key):
        # Decodifica la clave desde Base64
        if isinstance(key, str):
            key = base64.urlsafe_b64decode(key.encode())
        # Asegura que la clave tenga 16, 24 o 32 bytes
        if len(key) not in [16, 24, 32]:
            raise ValueError("La clave debe tener 16, 24 o 32 bytes")
        self.key = key

    def encrypt(self, data):
        # Convierte los datos a bytes si no lo están
        if isinstance(data, str):
            data = data.encode()
        # Genera un IV aleatorio
        iv = get_random_bytes(AES.block_size)
        # Crea el cifrador AES en modo CBC
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        # Cifra los datos
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))
        # Combina el IV y los datos cifrados
        return base64.urlsafe_b64encode(iv + encrypted_data).decode()

    def decrypt(self, encrypted_data):
        # Decodifica los datos cifrados
        encrypted_data = base64.urlsafe_b64decode(encrypted_data)
        # Extrae el IV
        iv = encrypted_data[:AES.block_size]
        # Extrae los datos cifrados
        encrypted_data = encrypted_data[AES.block_size:]
        # Crea el cifrador AES en modo CBC
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        # Descifra los datos
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        # Devuelve los datos como string
        return decrypted_data.decode()
    

    @staticmethod
    def generate_base64_key():
        key = os.urandom(32)
        key_base64 = base64.urlsafe_b64encode(key).decode()
        print("Clave AES generada:", key_base64)
    
    @staticmethod
    def test_cifrado(correo:str = "juan@example.com"):
        
        load_dotenv()
        cipher = AESCipher(os.getenv("FERNET_KEY"))

        correo_cifrado = cipher.encrypt(correo)
        print("Correo cifrado:", correo_cifrado)

        correo_descifrado = cipher.decrypt(correo_cifrado)
        print("Correo descifrado:", correo_descifrado)

    @staticmethod
    def cifrar_datos(dato:str = "juan@example.com"):
        
        load_dotenv()
        cipher = AESCipher(os.getenv("FERNET_KEY"))

        dato_cifrado = cipher.encrypt(dato)
        print("dato cifrado:", dato_cifrado)

        dato_descifrado = cipher.decrypt(dato_cifrado)
        print("dato descifrado:", dato_descifrado)
        
        return dato_cifrado

if __name__ == "__main__":
    AESCipher.test_cifrado()
