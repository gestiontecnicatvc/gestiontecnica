from .entities.User import User
import psycopg2
import psycopg2.extras

DB_HOST = "127.0.0.1"
DB_NAME = "gestion_tecnica"
DB_USER = "postgres"
#DB_PASS = "12345678"
DB_PASS = "gestion2022"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST) 

class ModelUser():

    @classmethod
    def login(self, user):
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            sql = """SELECT lo_id, lo_username, lo_password, lo_fullname FROM log_in 
                    WHERE lo_username = '{}'""".format(user.username)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                user = User(row[0], row[1], User.check_password(row[2], user.password), row[3])
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(self, db, id):
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            #cursor = db.connection.cursor()
            sql = "SELECT lo_id, lo_username, lo_fullname FROM log_in WHERE lo_id = {}".format(id)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                return User(row[0], row[1], None, row[2])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
