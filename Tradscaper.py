import time
from io import StringIO
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests

# =====================================================
# SETTINGS
# =====================================================

LOOP_DURATION = 1      # Seconds between runs
INTERVAL = 1            # Number of runs

TIMEZONE = ZoneInfo("Asia/Karachi")

# =====================================================
# OUTPUT FILE (GitHub Friendly)
# =====================================================

today = datetime.now(TIMEZONE)

OUTPUT_DIR = (
    Path("Trading")
    / "data"
    / str(today.year)
    / f"{today.month:02d}"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / f"{today:%Y-%m-%d}.xlsx"

# =====================================================
# PSX URL
# =====================================================

URL = "https://dps.psx.com.pk/trading-board/REG/main"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml",
    "Referer": "https://dps.psx.com.pk/trading-panel"
}

# =====================================================
# MAIN LOOP
# =====================================================

print("=" * 70)
print("PSX TRADING BOARD DATA COLLECTOR")
print("=" * 70)
print(f"Loop Duration : {LOOP_DURATION} seconds")
print(f"Total Runs    : {INTERVAL}")
print(f"Output File   : {OUTPUT_FILE}")
print("=" * 70)

for run_no in range(1, INTERVAL + 1):

    now = datetime.now(TIMEZONE)

    print(f"\n[{now:%Y-%m-%d %H:%M:%S}]")
    print(f"Starting Run {run_no} of {INTERVAL}")

    try:

        # -------------------------------------------------
        # DOWNLOAD DATA
        # -------------------------------------------------

        response = requests.get(
            URL,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        print(f"Status Code: {response.status_code}")

        # -------------------------------------------------
        # READ HTML TABLE
        # -------------------------------------------------

        tables = pd.read_html(
            StringIO(response.text)
        )

        if not tables:
            raise Exception("No HTML tables found")

        df_new = tables[0]

        # -------------------------------------------------
        # CLEAN COLUMNS
        # -------------------------------------------------

        df_new.columns = [
            str(col).strip()
            for col in df_new.columns
        ]

        # -------------------------------------------------
        # ADD DATE STAMP
        # -------------------------------------------------

        df_new["DATE_STAMP"] = now.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # -------------------------------------------------
        # APPEND TO EXISTING DATA
        # -------------------------------------------------

        if OUTPUT_FILE.exists():

            try:

                df_existing = pd.read_excel(
                    OUTPUT_FILE,
                    engine="openpyxl"
                )

                df_final = pd.concat(
                    [df_existing, df_new],
                    ignore_index=True
                )

                print(
                    f"Existing Rows: {len(df_existing):,}"
                )

            except Exception as e:

                print(
                    f"Could not read existing file: {e}"
                )

                df_final = df_new.copy()

        else:

            print("Creating new daily Excel file...")

            df_final = df_new.copy()

        # -------------------------------------------------
        # SAVE FILE
        # -------------------------------------------------

        df_final.to_excel(
            OUTPUT_FILE,
            index=False,
            engine="openpyxl"
        )

        print(f"New Rows Added : {len(df_new):,}")
        print(f"Total Rows     : {len(df_final):,}")
        print(f"Saved To       : {OUTPUT_FILE}")

    except Exception as e:

        print("\nERROR OCCURRED")
        print(str(e))

    # -------------------------------------------------
    # WAIT
    # -------------------------------------------------

    if run_no < INTERVAL:

        print(
            f"\nWaiting {LOOP_DURATION} seconds before next run..."
        )

        time.sleep(LOOP_DURATION)

# =====================================================
# FINISHED
# =====================================================

print("\n" + "=" * 70)
print("ALL RUNS COMPLETED")
print("=" * 70)
print(f"Output Saved To:\n{OUTPUT_FILE}")
