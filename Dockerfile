# Playwright と各ブラウザが pre-installed な公式 Python イメージ
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# 作業ディレクトリを設定
WORKDIR /app

# requirements.txt をコピーして依存関係をインストール
COPY requirements.txt .
RUN pip install -r requirements.txt

# ソースコードをコピー
COPY . .

# Playwright のキャッシュディレクトリを設定（任意）
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# アプリ起動スクリプト
CMD ["bash", "start.sh"]
