import os
import base64
import asyncio
import pandas as pd
import gspread
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from playwright.async_api import async_playwright

creds_base64 = os.environ["GOOGLE_CREDS_BASE64"]
with open("credentials.json", "wb") as f:
    f.write(base64.b64decode(creds_base64))

LOGIN_ID = os.getenv("LOGIN_ID")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")

async def run(playwright):
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(accept_downloads=True)
    page = await context.new_page()

    await page.goto("https://yuzupilates-admin.hacomono.jp/#/auth/")

    # ログイン
    await page.fill('input[type="text"]', LOGIN_ID)
    await page.fill('input[type="password"]', LOGIN_PASSWORD)
    await page.get_by_role("button", name=" ログイン").click()

    # 「閉じる」があれば閉じる
    try:
        await page.get_by_role("button", name="閉じる").click()
    except:
        pass  # なければ無視してOK

    # ログイン完了後に直接「データ集計」に遷移
    await page.goto("https://yuzupilates-admin.hacomono.jp/#/analysis/queries/")
    await page.get_by_role("link", name="メンバー一覧", exact=True).wait_for(state="visible")
    await page.get_by_role("link", name="メンバー一覧", exact=True).click()

    # 店舗選択（飯田橋店）
    await page.get_by_text("飯田橋店").wait_for(state="visible")
    await page.get_by_text("飯田橋店").click()
    await page.locator("a").filter(has_text="S0028 飯田橋店").wait_for(state="visible")
    await page.locator("a").filter(has_text="S0028 飯田橋店").click()

    # 検索 → エクスポート
    await page.get_by_role("button", name="検索").wait_for(state="visible")
    await page.get_by_role("button", name="検索").click()
    await page.get_by_role("button", name="エクスポート").wait_for(state="visible")
    await page.get_by_role("button", name="エクスポート").click()

    # ダウンロード取得
    async with page.expect_download() as download_info:
        await page.get_by_role("button", name="ダウンロード").click()
    download = await download_info.value
    file_path = await download.path()
    print(f"Downloaded CSV: {file_path}")

    # CSVを読み込み
    df = pd.read_csv(file_path, encoding="utf-8")
    
    # NaN や ±inf を空文字に変換（Google Sheetsに適した形）
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna("", inplace=True)
    
    # Google Sheets APIでアップロード
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

    await context.close()
    await browser.close()
    print("処理完了しました！")

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == "__main__":
    asyncio.run(main())
