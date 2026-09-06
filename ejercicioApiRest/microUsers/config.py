import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://{user}:{password}@{host}/{database}'.format(
            user=os.getenv('DB_USER'),
            password=quote_plus(os.getenv('DB_PASSWORD', '')),
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME')
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

