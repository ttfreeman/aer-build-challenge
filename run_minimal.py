"""Minimal run script: process all records through the pipeline."""
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from src.engine import TriageEngine

ROOT = Path(__file__).resolve().parent
load_dotenv()

console = Console()


def main():
    records_path = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "data" / "intake_records.json")
    
    # Load records
    with open(records_path) as f:
        data = json.load(f)
    records = data.get("records", [])
    
    console.print(f"[bold]Minimal Modular Triage Pipeline[/bold] - {len(records)} records\n")
    
    # Process
    engine = TriageEngine(traces_dir=ROOT / "traces")
    results = []
    
    for idx, record in enumerate(records, 1):
        result = engine.process_record(record)
        results.append(result.model_dump())
        console.print(f"[{idx}/{len(records)}] {record['record_id']} → {result.severity_tier} → {result.route}")
        if result.human_flag:
            console.print(f"  ⚠️  {result.human_flag_reason}")
    
    # Write results
    output_file = ROOT / "data" / "output_results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(results, indent=2))
    
    # Summary table
    console.print("\n[bold]Summary[/bold]")
    table = Table(title="Triage Results")
    table.add_column("Tier", style="cyan")
    table.add_column("Count", style="magenta")
    
    tier_counts = {}
    for r in results:
        tier = r["severity_tier"]
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    for tier in ["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Untiered"]:
        if tier in tier_counts:
            table.add_row(tier, str(tier_counts[tier]))
    
    console.print(table)
    console.print(f"\n✅ Results written to {output_file}")
    console.print(f"📄 Traces written to {ROOT / 'traces'}")


if __name__ == "__main__":
    main()
