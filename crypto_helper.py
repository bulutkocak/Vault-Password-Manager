import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets
import string

class CryptoHelper:
    def __init__(self, master_password):
        self.master_password = master_password.encode()
        self.salt = b'fixed_salt_123456'
    
    def _derive_key(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.master_password)
    
    def encrypt(self, plain_text):
        if not plain_text:
            return ""
        
        key = self._derive_key()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        encrypted = encryptor.update(plain_text.encode()) + encryptor.finalize()
        combined = iv + encrypted
        return base64.b64encode(combined).decode()
    
    def decrypt(self, cipher_text):
        if not cipher_text:
            return ""
        
        try:
            combined = base64.b64decode(cipher_text.encode())
            iv = combined[:16]
            encrypted = combined[16:]
            
            key = self._derive_key()
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            decrypted = decryptor.update(encrypted) + decryptor.finalize()
            return decrypted.decode()
        except:
            return None
    
    @staticmethod
    def generate_strong_password(length=16):
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        specials = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        all_chars = uppercase + lowercase + digits + specials
        
        password = [
            secrets.choice(uppercase),
            secrets.choice(lowercase),
            secrets.choice(digits),
            secrets.choice(specials)
        ]
        
        password.extend(secrets.choice(all_chars) for _ in range(length - 4))
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)