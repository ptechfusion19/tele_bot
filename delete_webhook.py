import asyncio
from aiogram import Bot

TOKEN = "8016112194:AAEYKqbIHjIHnqd-T77JktYG2C8vJVCsqHE"  

async def delete_webhook():
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook deleted successfully.")

if __name__ == "__main__":
    asyncio.run(delete_webhook())
