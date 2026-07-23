import os
from transformers import pipeline

# NER model load karo (naam, jagah detect karne ke liye)
print("Loading PII detection model... please wait")
ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

# Paths - root folder se relative (kyunki script src/ ke andar hai)
input_folder = "data/cleaned"
output_folder = "data/pii_removed"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def remove_pii(text):
    entities = ner(text)
    for ent in entities:
        if ent['entity_group'] in ['PER', 'LOC']:
            text = text.replace(ent['word'], "[REDACTED]")
    return text

files = os.listdir(input_folder)
count = 0

for filename in files:
    if filename.endswith(".txt"):
        filepath = os.path.join(input_folder, filename)
        
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        
        safe_text = remove_pii(text)
        
        output_path = os.path.join(output_folder, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(safe_text)
        
        count += 1
        print(f"Processed: {filename}")

print(f"\nDone! {count} files processed and saved in '{output_folder}' folder")