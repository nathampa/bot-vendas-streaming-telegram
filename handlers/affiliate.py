from aiogram import Router, types, F, Bot
from aiogram.types import Message
from core.config import settings

router = Router()

TEXTO_AFILIADO = """
👥 Programa de Afiliados

Convide seus amigos para o bot e ganhe prêmios!

Seu link de convite pessoal é:
`{link}`

Como funciona?
1. Seu amigo deve entrar no bot pela primeira vez usando o seu link.
2. Quando ele fizer a primeira {gatilho}, você ganha {premio}!

Compartilhe seu link e comece a ganhar!
"""

@router.message(F.text == "👥 Indique e Ganhe")
async def handle_affiliate_menu(message: Message, bot: Bot):
    user_id = message.from_user.id
    
    try:
        # Pega o username do bot (ex: @MeuBot)
        bot_user = await bot.get_me()
        bot_username = bot_user.username
    except Exception:
        await message.answer("Erro ao gerar seu link. Tente novamente.")
        return

    # Gera o link no formato: t.me/NomeDoBot?start=ref_12345678
    link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    # TODO: No futuro, podemos buscar as regras (gatilho/premio) da API
    # Por enquanto, usamos um texto genérico:
    texto_gatilho = "recarga ou compra"
    texto_premio = "um super prêmio"

    await message.answer(
        TEXTO_AFILIADO.format(
            link=link,
            gatilho=texto_gatilho,
            premio=texto_premio
        ),
        disable_web_page_preview=True
    )