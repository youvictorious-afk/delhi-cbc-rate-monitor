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
        await page.wait_for_timeout(15000)

        # Extra time for Power BI report
        await page.wait_for_timeout(15000)

        all_text = []

        # Main page text
        try:
            main_text = await page.locator("body").inner_text(
                timeout=30000
            )

            all_text.append(
                "\n===== MAIN PAGE =====\n"
            )

            all_text.append(main_text)

        except Exception as e:

            print(
                "Main page text error:",
                e
            )

        # Inspect every iframe/frame
        print(
            f"Frames detected: {len(page.frames)}"
        )

        for index, frame in enumerate(page.frames):

            try:

                print(
                    f"Reading frame {index}: "
                    f"{frame.url}"
                )

                frame_text = await frame.locator(
                    "body"
                ).inner_text(
                    timeout=20000
                )

                if frame_text.strip():

                    all_text.append(
                        f"\n===== FRAME {index} =====\n"
                    )

                    all_text.append(
                        frame_text
                    )

            except Exception as e:

                print(
                    f"Frame {index} error:",
                    e
                )

        # Combine everything
        text = "\n".join(all_text)

        html = await page.content()

        # Screenshot
        await page.screenshot(
            path=str(SCREENSHOT_PATH),
            full_page=True
        )

        # Save HTML
        HTML_PATH.write_text(
            html,
            encoding="utf-8"
        )

        # Save extracted text
        RAW_TEXT_PATH.write_text(
            text,
            encoding="utf-8"
        )

        print(
            "Collected text length:",
            len(text)
        )

        await browser.close()

        return {
            "checked_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "text": text
        }
