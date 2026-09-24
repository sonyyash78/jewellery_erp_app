import pymysql
from app.core.config import settings

def create_database_if_not_exists():
    # Parse the database URL to get connection details
    # mysql+pymysql://root:root1234%40@localhost:3306/jewellery_erp
    
    url = settings.DATABASE_URL
    if not url.startswith("mysql"):
        return
        
    try:
        # Strip "mysql+pymysql://"
        auth_host, db_name = url.split("://")[1].split("/")
        auth, host_port = auth_host.split("@")
        user, password = auth.split(":")
        
        # URL decode password
        import urllib.parse
        password = urllib.parse.unquote(password)
        
        host, port = host_port.split(":")
        
        # Connect to MySQL server without selecting a database
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password
        )
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            connection.commit()
            print(f"Database {db_name} ensured to exist.")
        finally:
            connection.close()
    except Exception as e:
        print(f"Error checking/creating database: {e}")
