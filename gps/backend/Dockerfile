# ベースイメージ
FROM python:3.11

# 作業ディレクトリを作成
WORKDIR /code

# Pythonの依存ファイルをコピー
COPY requirements.txt .

# 依存ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリコードをコピー
COPY . .

# ポートを開放（開発用）
EXPOSE 8000

# アプリ起動コマンド
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]