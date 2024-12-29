import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_test_database():
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create test database if it doesn't exist
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='test_db'")
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE test_db")
            print("Test database created successfully!")
        else:
            print("Test database already exists!")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_test_database() 