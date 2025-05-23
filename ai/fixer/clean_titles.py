import pandas as pd
import inflect
import re
from typing import Tuple

p = inflect.engine()

def clean_job_title(title: str) -> Tuple[str, str]:
    """Returns (cleaned_title, transformation_note)"""
    original = title.strip()
    
    # Common replacements
    replacements = [
        (r", Except Gambling", ""),
        (r", All Other", ""),
        (r", Preschool and Daycare", ""),
        (r" and ", " & "),
    ]
    
    for pattern, repl in replacements:
        original = re.sub(pattern, repl, original)
    
    # Handle plurals in the last word
    words = original.split()
    if len(words) > 0:
        last_word = words[-1]
        singular = p.singular_noun(last_word)
        if singular:
            words[-1] = singular
            transformation = f"plural '{last_word}' → '{singular}'"
        else:
            transformation = "no plural detected"
    
    cleaned = " ".join(words)
    return cleaned, transformation

def process_excel(input_file: str) -> pd.DataFrame:
    df = pd.read_excel(input_file)
    
    results = []
    for _, row in df.iterrows():
        cleaned, note = clean_job_title(row['Title'])
        results.append({
            'original_code': row['O*NET-SOC Code'],
            'original_title': row['Title'],
            'standardised_title': cleaned,
            'transformation_note': note
        })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    df = process_excel("job_titles.xlsx")
    df.to_excel("cleaned_job_titles.xlsx", index=False)
    print("Cleaning complete. Saved to cleaned_job_titles.xlsx")