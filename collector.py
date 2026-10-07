from datetime import datetime, timezone

from playwright.async_api import async_playwright

from config import (
    CBC_URL,
    RAW_TEXT_PATH,
    SCREENSHOT_PATH,
    HTML_PATH
)


async def collect_cbc_report():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        page = await browser.new_page(
            viewport={
                "width": 1600,
                "height": 1200
            }
        )

        print("Opening CBC website...")

        await page.goto(
            CBC_URL,
            wait_until="domcontentloaded",
            timeout=120000
        )

        print("CBC page loaded")

        # Allow Power BI to initialise
        await page.wait_for_timeout(20000)

        print(
            "Total frames:",
            len(page.frames)
        )

        all_text = []

        for index, frame in enumerate(page.frames):

            print(
                f"\n===== FRAME {index} ====="
            )

            print(
                "URL:",
                frame.url
            )

            try:

                title = await frame.title()

                print(
                    "TITLE:",
                    title
                )

            except Exception as e:

                print(
                    "Title error:",
                    e
                )

            try:

                body = frame.locator("body")

                text = await body.inner_text(
                    timeout=30000
                )

                print(
                    "TEXT LENGTH:",
                    len(text)
                )

                if text.strip():

                    all_text.append(
                        f"\n===== FRAME {index} =====\n"
                    )

                    all_text.append(text)

            except Exception as e:

                print(
                    "BODY ERROR:",
                    e
                )

        # Take screenshot of complete page
        await page.screenshot(
            path=str(SCREENSHOT_PATH),
            full_page=True
        )

        # Save complete HTML
        html = await page.content()

        HTML_PATH.write_text(
            html,
            encoding="utf-8"
        )

        # Combined text
        text = "\n".join(all_text)

        RAW_TEXT_PATH.write_text(
            text,
            encoding="utf-8"
        )

        print(
            "\nTOTAL TEXT LENGTH:",
            len(text)
        )

        await browser.close()

        return {
            "checked_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "text": text
        }
