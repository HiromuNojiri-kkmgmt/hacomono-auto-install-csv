import os
import time
import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import gspread
from oauth2client.service_account import ServiceAccountCredentials

LOGIN_ID = os.getenv("LOGIN_ID")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")

async def run(playwright):
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(accept_downloads=True)
    page = await context.new_page()

    print("Logging in...")
    await page.goto("https://YOUR_ADMIN_URL/login")  # ←管理画面URLに書き換えてください
    await page.fill('input[type="email"]', LOGIN_ID)
    await page.fill('input[type="password"]', LOGIN_PASSWORD)
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("networkidle")
    
    print("Navigating to export page...")
    await page.goto("https://YOUR_ADMIN_URL/customers")  # ←顧客一覧ページに書き換えてください
    await page.wait_for_load_state("networkidle")

    print("Waiting for export button...")
    export_button = await page.wait_for_selector('button:has-text("エクスポート")')
    async with page.expect_download() as download_info:
        await export_button.click()
    download = await download_info.value
    file_path = await download.path()
    file_name = download.suggested_filename
    print(f"Downloaded: {file_name}")

    # CSV読み込み
    df = pd.read_csv(file_path, encoding="utf-8")

    # Google Sheetsへアップロード
    print("Uploading to Google Sheets...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("Upload complete.")

    await context.close()
    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())