import json
import os
import sys
from dotenv import load_dotenv
from src.aer_triage_agent import AERTriageEngine

def main():
    load_dotenv()

    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY environment variable not set.")
        return

    # Get intake records file path from command-line argument or use default
    intake_file = sys.argv[1] if len(sys.argv) > 1 else 'data/intake_records.json'
    
    if not os.path.exists(intake_file):
        print(f"ERROR: Intake records file not found: {intake_file}")
        return

    print("Initializing AER Triage Engine & Local Vector DB...")
    engine = AERTriageEngine()

    print(f"Loading intake records from {intake_file}...")
    with open(intake_file, 'r') as f:
        data = json.load(f)

    records = data.get('records', [])
    print(f"Executing batch run on {len(records)} records...\n")
    print("-" * 80)
    
    results_list = []
    
    for idx, record in enumerate(records, start=1):
        print(f"[{idx}/{len(records)}] Processing {record['record_id']}...")
        
        result = engine.process_record(record)
        results_list.append(result.model_dump())
        
        print(f"   └─ Tier: {result.severity_tier}")
        print(f"   └─ Route: {result.route}")
        if result.human_flag:
            print(f"   └─ ⚠️ HUMAN FLAG: {result.human_flag_reason}")
        print(f"   └─ Latency: {result.run_record['execution_latency_sec']}s\n")

    output_file = "data/output_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results_list, f, indent=2)

    print("-" * 80)
    print(f"✅ Batch execution complete. Full trace output saved to {output_file}.")

if __name__ == "__main__":
    main()
