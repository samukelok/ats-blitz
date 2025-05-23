import pandas as pd
import mysql.connector
from config import DB_CONFIG

def import_data():
    df = pd.read_excel("cleaned_job_titles.xlsx")
    
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    insert_query = """
    INSERT INTO standardised_job_titles 
    (original_code, original_title, standardised_title)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE
    standardised_title = VALUES(standardised_title)
    """
    
    for _, row in df.iterrows():
        cursor.execute(insert_query, (
            row['original_code'],
            row['original_title'],
            row['standardised_title']
        ))
    
    conn.commit()
    print(f"Imported {len(df)} records")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    import_data()