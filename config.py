from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

CBC_URL = "https://cbcindia.gov.in/publishers-on-panel/"

DATABASE_PATH = DATA_DIR / "rates.db"

RAW_TEXT_PATH = DATA_DIR / "cbc_raw_text.txt"

SCREENSHOT_PATH = DATA_DIR / "cbc_report.png"

HTML_PATH = DATA_DIR / "cbc_report.html"
