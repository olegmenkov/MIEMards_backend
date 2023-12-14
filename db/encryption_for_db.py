from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os


def encrypt(string):
    password = bytes(string, 'utf-8')
    load_dotenv()
    key = bytes(str(os.getenv('ENC_KEY')), 'utf-8')
    f = Fernet(key)
    return f.encrypt(password)


def decrypt(string):
    load_dotenv()
    key = bytes(str(os.getenv('ENC_KEY')), 'utf-8')
    f = Fernet(key)
    return f.decrypt(string).decode('utf-8')
