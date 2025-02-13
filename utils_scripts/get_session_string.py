from pyrogram import Client

from config import Config

if __name__ == "__main__":
    with Client("session_name", Config.API_ID, Config.API_HASH) as app:
        print("Это session_string, укажи его в .env")
        print(app.export_session_string())
