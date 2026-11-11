from passlib.context import CryptContext

class HashService:
    SECRET_KEY = "abcde"

    def __init__(self,pwd_context:CryptContext):
        self.pwd_context=pwd_context

    def hash_password(self,password:str) -> str:   
        # encrypting the password
        password_concat=password + self.SECRET_KEY
        return self.pwd_context.hash(password_concat)

    def verify_hash_password(self , password:str,hash_password:str) -> Boolean:
        password_concat=password + self.SECRET_KEY
        return self.pwd_context.verify(password_concat,hash_password)
    