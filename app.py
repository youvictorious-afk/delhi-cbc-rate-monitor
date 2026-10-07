from io import BytesIO

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
    version="1.0"
)


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


@app.post("/fetch")
async def fetch_rates():

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

    return {

        "status": "success",

        "checked_at":
            result["checked_at"],

        "delhi_records_found":
            len(rows),

        "records_saved":
            saved
    }


@app.get("/rates")
def rates():

    return {
        "scope": "DELHI ONLY",

        "rows":
            get_latest()
    }


@app.get("/history")
def history():

    return {
        "scope": "DELHI ONLY",

        "rows":
            get_history()
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
            "attachment; "
            'filename="Delhi_CBC_Rates.xlsx"'
        }
    )
