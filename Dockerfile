FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir pyrogram tgcrypto aiohttp aiofiles flask python-dotenv

EXPOSE 8080
CMD ["python3", "bot.py"]
