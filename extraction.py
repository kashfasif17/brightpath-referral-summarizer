import os
import ollama

input_folder = "data/pii_removed"
output_folder = "data/extracted_summaries"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def build_prompt(letter_text):
    return f"""Extract the following fields from this referral letter and return ONLY valid JSON, nothing else, no markdown formatting, no explanation:
- age
- gender
- chief_complaint
- medical_history
- suspected_diagnosis
- referral_reason

Letter:
{letter_text}
"""

files = os.listdir(input_folder)
count = 0

for filename in files:
    if filename.endswith(".txt"):
        filepath = os.path.join(input_folder, filename)
        
        with open(filepath, "r", encoding="utf-8") as f:
            letter_text = f.read()
        
        prompt = build_prompt(letter_text)
        
        print(f"Processing: {filename} (this may take a minute)...")
        
        try:
            response = ollama.chat(model='phi3', messages=[
                {'role': 'user', 'content': prompt}
            ])
            result_text = response['message']['content']
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
        
        output_filename = filename.replace(".txt", ".json")
        output_path = os.path.join(output_folder, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result_text)
        
        count += 1
        print(f"Done ({count}/{len(files)}): {filename}\n")

print(f"\nAll done! {count} letters processed and saved in '{output_folder}' folder")