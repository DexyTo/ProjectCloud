import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    YC_ACCESS_KEY = os.getenv('YC_ACCESS_KEY')
    YC_SECRET_KEY = os.getenv('YC_SECRET_KEY')
    YC_BUCKET_NAME = os.getenv('YC_BUCKET_NAME')
    YC_ENDPOINT_URL = os.getenv('YC_ENDPOINT_URL')
    

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f'mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


config = Config()