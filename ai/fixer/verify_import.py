import pandas as pd
import mysql.connector
from config import DB_CONFIG

def verify_import():
    conn = mysql.connector.connect(**DB_CONFIG)
    
    # Compare counts
    mysql_count = pd.read_sql("SELECT COUNT(*) FROM standardised_job_titles", conn).iloc[0,0]
    excel_count = len(pd.read_excel("cleaned_job_titles.xlsx"))
    
    print(f"MySQL records: {mysql_count} | Excel records: {excel_count}")
    
    # Sample verification
    sample = pd.read_sql("""
    SELECT original_title, standardised_title 
    FROM standardised_job_titles
    WHERE original_title != standardised_title
    LIMIT 5
    """, conn)
    
    print("\nSample transformations:")
    print(sample)
    
    conn.close()

if __name__ == "__main__":
    verify_import()