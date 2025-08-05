# 自動CSVエクスポート & Google Sheets アップロード

## 概要

このプロジェクトは、Playwrightを使ってログイン制の管理画面から顧客CSVを自動で取得し、Google Sheetsにアップロードする処理を行います。Renderでデプロイし、外部cronサービスで毎日自動実行します。

## 必要な環境変数

Render上で以下を設定してください：

- `LOGIN_ID`: 管理サイトのログインID
- `LOGIN_PASSWORD`: ログインパスワード
- `SPREADSHEET_ID`: 対象のスプレッドシートID
- `SHEET_NAME`: 書き込み対象のシート名

## ファイル構成

- `main.py`: メイン処理
- `start.sh`: Playwrightセットアップと起動スクリプト
- `requirements.txt`: ライブラリ定義
- `render.yaml`: Render設定
- `.gitignore`: `credentials.json`を除外

## Google Sheets API

`credentials.json` をプロジェクトに配置し、Render上にアップロードする工夫が必要です（例：一時的なURLからダウンロード、またはColabでアップ）。