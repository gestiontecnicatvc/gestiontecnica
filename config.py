class Config(object):
    SECRET_KEY = '*tvc_digit_2022'

class DevelopmentConfig(Config):
    DEBUG = True
    '''MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '123456'
    MYSQL_DB = 'flask_login'''

    DB_HOST = "127.0.0.1"
    DB_NAME = "gestion_tecnica"
    DB_USER = "postgres"
    DB_PASS = "12345678"

config = {
    'development': DevelopmentConfig
}
