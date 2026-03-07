import subprocess
import sys

years = [2020, 2021, 2022, 2023, 2024]

sources = {
    "FiinPro": "01-20",
    "BCTC_Audited": "03-31",
    "Vietstock": "01-05",
    "AnnualReport": "04-15"
}

def run_command(cmd):
    try:
        result = subprocess.run(cmd, check=True, text=True)
        print("✅ Success\n")
    except subprocess.CalledProcessError as e:
        print("❌ Error running:", " ".join(cmd))
        print(e)
        print("Continuing...\n")

def main():
    print("=== INITIALIZING SNAPSHOTS ===\n")

    for year in years:
        for source, date_suffix in sources.items():

            snapshot_date = f"{year+1}-{date_suffix}"

            cmd = [
                sys.executable,   # đảm bảo dùng đúng python env
                "create_snapshot.py",
                "--source", source,
                "--year", str(year),
                "--date", snapshot_date,
                "--version", "v1_raw"
            ]

            print("Running:", " ".join(cmd))
            run_command(cmd)

    print("=== DONE INITIALIZING SNAPSHOTS ===")

if __name__ == "__main__":
    main()