import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    total_records = len(records)
    print(f"Executing concurrent batch run on {total_records} records...\n")
    print("-" * 80)
    
    results_list = []
    start_time = time.time()
    
    # Process up to 10 records concurrently to stay under standard API rate limits
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all records to the executor
        future_to_record = {executor.submit(engine.process_record, rec): rec for rec in records}
        
        # Process results as they complete
        for completed_count, future in enumerate(as_completed(future_to_record), start=1):
            record = future_to_record[future]
            try:
                result = future.result()
                results_list.append(result.model_dump())

                print(f"[{completed_count}/{total_records}] ✅ Processed {result.record_id} in {result.run_record['execution_latency_sec']}s")
                print(f"   └─ Tier: {result.severity_tier} | Route: {result.route}")
                if result.human_flag:
                    print(f"   └─ ⚠️ HUMAN FLAG: {result.human_flag_reason}")
                print()

            except Exception as exc:
                print(f"[{completed_count}/{total_records}] ❌ FAILED {record['record_id']} - Exception: {exc}\n")

    total_time = round(time.time() - start_time, 2)

    # Save the output to a JSON artifact
    output_file = "data/output_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results_list, f, indent=2)

    print("-" * 80)
    print(f"✅ Batch execution complete in {total_time} seconds. Full trace output saved to {output_file}.")

if __name__ == "__main__":
    main()
