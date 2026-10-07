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
            headless=True
        )

        page = await browser.new_page(
            viewport={
                "width": 1600,
                "height": 1000
            }
        )

        await page.goto(
            CBC_URL,
            wait_until="domcontentloaded",
            timeout=120000
        )

        # Give CBC page and embedded Power BI time to load.
        await page.wait_for_timeout(15000)

        # Additional rendering time.
        await page.wait_for_timeout(10000)

        text = await page.locator("body").inner_text()

        html = await page.content()

        await page.screenshot(
            path=str(SCREENSHOT_PATH),
            full_page=True
        )

        RAW_TEXT_PATH.write_text(
            text,
            encoding="utf-8"
        )

        HTML_PATH.write_text(
            html,
            encoding="utf-8"
        )

        await browser.close()

        return {
            "checked_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "text": text
        }
