import asyncio
import logging
import sys
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.enums import ParseMode

# Importa as nossas configurações (o Token!)
from core.config import settings

# Importa os nossos manipuladores de comandos
from handlers import common, wallet, catalog, purchase, support, giftcard, suggestions

# Seta a lista dos comandos, para exibir o menu azul
async def set_bot_commands(bot: Bot):
    """
    Define a lista de comandos que aparece no botão "Menu" do Telegram.
    """
    commands = [
        BotCommand(command="start", description="▶️ Iniciar o bot"),
        BotCommand(command="produtos", description="🛍️ Ver Produtos"),
        BotCommand(command="carteira", description="💳 Ver Carteira/Adicionar Saldo"),
        BotCommand(command="resgatar", description="🎁 Resgatar Código"),
        BotCommand(command="suporte", description="🆘 Abrir ticket de Suporte"),
        BotCommand(command="sugerir", description="💡 Fazer uma sugestão"),
    ]
    await bot.set_my_commands(commands)

async def main():
    # 1. Cria o objeto Bot com o nosso token
    bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
    
    # 2. Cria o Dispatcher (distribuidor de mensagens)
    dp = Dispatcher()

    # 3. Regista os nossos roteadores (handlers)
    # (Por agora, apenas os comandos comuns como /start)
    dp.include_router(common.router)
    dp.include_router(wallet.router)
    dp.include_router(catalog.router)
    dp.include_router(purchase.router)
    dp.include_router(support.router)
    dp.include_router(giftcard.router)
    dp.include_router(suggestions.router)

    # 4. Limpa webhooks pendentes (boa prática)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # 5. Inicia o "polling" (o bot começa a "ouvir" o Telegram)
    print("Bot a iniciar...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Configura o logging para vermos o que se passa
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    try:
        # Inicia a função 'main' assíncrona
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot desligado.")