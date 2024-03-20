from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

from loguru import logger


def encrypt(string):
    load_dotenv()
    key = bytes(str(os.getenv('ENC_KEY')), 'utf-8')
    f = Fernet(key)
    password = bytes(string, 'utf-8')
    return f.encrypt(password)


def decrypt(string):
    try:
        load_dotenv()
        key = bytes(str(os.getenv('ENC_KEY')), 'utf-8')
        f = Fernet(key)
        decrypted_data = f.decrypt(string)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        logger.debug(f"Error during decryption: {e}")
        return None
