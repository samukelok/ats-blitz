import mysql.connector
from config import DB_CONFIG

def initialize_database():
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    cursor = conn.cursor()
    
    # Create database
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    cursor.execute(f"USE {DB_CONFIG['database']}")
    
    # Create table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS standardised_job_titles (
        id INT AUTO_INCREMENT PRIMARY KEY,
        original_code VARCHAR(20) NOT NULL,
        original_title VARCHAR(255) NOT NULL,
        standardised_title VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY (original_code)
    )""")
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    initialize_database()
    print("Database initialised successfully")