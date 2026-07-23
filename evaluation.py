import os
import json

input_folder = "data/extracted_summaries"

expected_fields = [
    "age", "gender", "chief_complaint",
    "medical_history", "suspected_diagnosis", "referral_reason"
]

files = os.listdir(input_folder)
total_files = 0
valid_json_count = 0
completeness_scores = []

results_report = []

for filename in files:
    if filename.endswith(".json"):
        filepath = os.path.join(input_folder, filename)
        total_files += 1
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Metric 1: Kya valid JSON hai?
        try:
            data = json.loads(content)
            is_valid_json = True
            valid_json_count += 1
        except json.JSONDecodeError:
            is_valid_json = False
            data = {}
        
        # Metric 2: Kitne fields filled hain
        if is_valid_json:
            filled_count = 0
            for field in expected_fields:
                value = data.get(field, "")
                if value and str(value).strip() != "":
                    filled_count += 1
            completeness = filled_count / len(expected_fields)
        else:
            completeness = 0
        
        completeness_scores.append(completeness)
        
        results_report.append({
            "filename": filename,
            "valid_json": is_valid_json,
            "completeness_score": round(completeness, 2)
        })

# Overall summary calculate karo
avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
json_validity_rate = valid_json_count / total_files if total_files else 0

# Report print karo
print("=" * 50)
print("EVALUATION REPORT")
print("=" * 50)
print(f"Total files evaluated: {total_files}")
print(f"Valid JSON outputs: {valid_json_count}/{total_files} ({json_validity_rate*100:.1f}%)")
print(f"Average completeness score: {avg_completeness*100:.1f}%")
print("=" * 50)
print("\nPer-file breakdown:")
for r in results_report:
    status = "VALID" if r["valid_json"] else "INVALID"
    print(f"  {r['filename']}: {status}, completeness = {r['completeness_score']*100:.0f}%")

# Report ko file mein bhi save karo
with open("evaluation_report.json", "w", encoding="utf-8") as f:
    json.dump({
        "total_files": total_files,
        "valid_json_count": valid_json_count,
        "json_validity_rate": round(json_validity_rate, 2),
        "average_completeness": round(avg_completeness, 2),
        "details": results_report
    }, f, indent=2)

print("\nFull report saved to 'evaluation_report.json'")