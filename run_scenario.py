#!/usr/bin/env python3
"""
Simple scenario runner for mortgage calculator
Usage: python run_scenario.py [conservative|aggressive|high_loan]
"""

import sys
import shutil
from pathlib import Path
import subprocess

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_scenario.py [conservative|aggressive|high_loan]")
        print("\nAvailable scenarios:")
        print("  conservative - 2 cuts of 0.25% each (gradual)")
        print("  aggressive   - 4 cuts of 0.25% each (front-loaded)")
        print("  high_loan    - $1M loan with 5-year analysis")
        sys.exit(1)

    scenario = sys.argv[1].lower()

    scenarios = {
        'conservative': 'conservative.env',
        'aggressive': 'aggressive.env',
        'high_loan': 'high_loan.env'
    }

    if scenario not in scenarios:
        print(f"Unknown scenario: {scenario}")
        print(f"Available scenarios: {', '.join(scenarios.keys())}")
        sys.exit(1)

    config_dir = Path(__file__).parent / "config"
    source_file = config_dir / scenarios[scenario]
    target_file = config_dir / "mortgage.env"

    if not source_file.exists():
        print(f"Scenario file not found: {source_file}")
        sys.exit(1)

    # Copy scenario file to active config
    shutil.copy2(source_file, target_file)
    print(f"Switched to {scenario} scenario")
    print(f"Running mortgage analysis...")
    print("-" * 50)

    # Run the mortgage calculator
    subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    main()