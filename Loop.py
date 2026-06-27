import time
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configuration
num_loops = 3
interval = 20  # seconds

# Scripts to run
SCRIPTS = [
    "Tradscaper.py",
    "Intrascaper.py",
    "indscraper.py"
]

def run_script(script):
    """Run a single Python script and handle errors."""
    try:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting {script}...")

        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            timeout=300  # 5-minute timeout
        )

        if result.returncode == 0:
            print(f"✓ {script} completed successfully.")
            if result.stdout.strip():
                print(result.stdout)
        else:
            print(f"✗ {script} failed with exit code {result.returncode}")
            if result.stderr.strip():
                print("Error output:")
                print(result.stderr)
            if result.stdout.strip():
                print("Standard output:")
                print(result.stdout)

    except subprocess.TimeoutExpired:
        print(f"✗ {script} timed out after 5 minutes.")
    except Exception as e:
        print(f"✗ Error running {script}: {e}")


def run_all_scripts():
    """Run all scripts sequentially."""
    for script in SCRIPTS:
        if Path(script).exists():
            run_script(script)
        else:
            print(f"⚠ File not found: {script}")


if __name__ == "__main__":
    print(f"Starting Auto Loop - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuration: {num_loops} loops with {interval}s interval")
    print(f"Scripts: {', '.join(SCRIPTS)}\n")

    for i in range(num_loops):
        print("\n" + "=" * 60)
        print(f"Loop {i + 1}/{num_loops}")
        print("=" * 60)

        run_all_scripts()

        if i < num_loops - 1:
            print(f"\nWaiting {interval} seconds until next loop...")
            time.sleep(interval)

    print("\n" + "=" * 60)
    print(f"All {num_loops} loops completed!")
    print("=" * 60)
