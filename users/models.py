import os
from django.db import models
from django.core.validators import RegexValidator
from dotenv import load_dotenv
from users.utils import AESCipher

load_dotenv()
cipher = AESCipher(os.getenv('FERNET_KEY'))

class User(models.Model):
    name = models.CharField(max_length=100, null=False)
    lastname = models.CharField(max_length=100, null=False)
    username = models.CharField(unique=True, max_length=100, null=False)
    password = models.TextField(max_length=255, null=False)  # Almacenará el password cifrado
    email = models.TextField(unique=True, blank=False)  # Almacenará el email cifrado
    cellphone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )
    team = models.CharField(max_length=100, blank=True, null=True)

    REQUIRED_FIELDS = ['name', 'lastname', 'username', 'password', 'email']

    def set_password(self, raw_password: str):
        """Cifra el password antes de guardarlo."""
        self.password = cipher.encrypt(raw_password)
    
    def get_password(self):
        """Descifra el password almacenado."""
        return cipher.decrypt(self.password)
    
    def set_email(self, raw_email: str):
        """Cifra el email antes de guardarlo."""
        self.email = cipher.encrypt(raw_email)

    def get_email(self):
        """Descifra el email almacenado."""
        return cipher.decrypt(self.email)
    
    # Propiedades para compatibilidad con DRF (sin necesidad de migración)
    @property
    def is_authenticated(self):
        """Siempre devuelve True para usuarios existentes"""
        return True
        
    @property
    def is_anonymous(self):
        """Siempre devuelve False para usuarios reales"""
        return False
    
    @property
    def is_active(self):
        return True  # O implementa lógica según tu campo 'team' u otro

    def __str__(self):
        return f"({self.username}) {self.name} {self.lastname}"