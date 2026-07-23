import os

def clean_text(text):
    """
    Referral letter text ko clean karta hai:
    - Extra spaces/blank lines hatata hai
    - Consistent formatting banata hai
    """
    lines = text.split("\n")
    lines = [line.strip() for line in lines if line.strip() != ""]
    cleaned = "\n".join(lines)
    return cleaned


def clean_all_files(input_folder="data", output_folder="data/cleaned"):
    """
    input_folder ke sab .txt files ko clean karke
    output_folder mein save karta hai
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    files = [f for f in os.listdir(input_folder) if f.endswith(".txt")]
    count = 0

    for filename in files:
        filepath = os.path.join(input_folder, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()

        cleaned_text = clean_text(raw_text)

        output_path = os.path.join(output_folder, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        count += 1
        print(f"Cleaned: {filename}")

    print(f"\nDone! {count} files cleaned and saved in '{output_folder}'")


if __name__ == "__main__":
    clean_all_files()