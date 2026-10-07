from io import BytesIO
import asyncio
import pandas as pd

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from collector import collect_cbc_report
from parser import extract_delhi_lines

from database import (
    init_database,
    insert_rate,
    get_history,
    get_latest
)

from config import CBC_URL


app = FastAPI(
    title="Delhi CBC Rate Monitor",
    version="1.2"
)

fetch_status = {
    "status": "idle",
    "message": "No fetch running",
    "checked_at": None,
    "records_found": 0
}


@app.on_event("startup")
def startup():
    init_database()


@app.get("/")
def home():
    return {
        "system": "Delhi CBC Rate Monitor",
        "status": "running",
        "scope": "DELHI ONLY",
        "source": CBC_URL
    }


@app.get("/health")
def health():
    return {
        "status": "OK",
        "scope": "DELHI ONLY"
    }


async def run_fetch():

    global fetch_status

    try:

        fetch_status = {
            "status": "running",
            "message": "Opening CBC and inspecting Power BI...",
            "checked_at": None,
            "records_found": 0
        }

        result = await collect_cbc_report()

        rows = extract_delhi_lines(
            result["text"]
        )

        saved = 0

        for row in rows:

            row["checked_at"] = result["checked_at"]
            row["source_url"] = CBC_URL

            insert_rate(row)

            saved += 1

        fetch_status = {
            "status": "completed",
            "message": "Fetch completed",
            "checked_at": result["checked_at"],
            "records_found": len(rows),
            "records_saved": saved
        }

    except Exception as e:

        fetch_status = {
            "status": "error",
            "message": str(e),
            "checked_at": None,
            "records_found": 0
        }


@app.get("/fetch")
async def fetch_rates():

    global fetch_status

    if fetch_status["status"] == "running":

        return {
            "status": "already_running",
            "message": "CBC fetch is already running",
            "check": "/fetch-status"
        }

    asyncio.create_task(
        run_fetch()
    )

    return {
        "status": "started",
        "message": "CBC fetch started in background",
        "check": "/fetch-status"
    }


@app.get("/fetch-status")
def fetch_status_endpoint():

    return fetch_status


@app.get("/rates")
def rates():

    return {
        "scope": "DELHI ONLY",
        "rows": get_latest()
    }


@app.get("/history")
def history():

    return {
        "scope": "DELHI ONLY",
        "rows": get_history()
    }


@app.get("/export.xlsx")
def export_excel():

    rows = get_history()

    df = pd.DataFrame(rows)

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Delhi Rate History"
        )

    output.seek(0)

    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
            'attachment; filename="Delhi_CBC_Rates.xlsx"'
        }
    )
