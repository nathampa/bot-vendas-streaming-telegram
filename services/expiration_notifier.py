import asyncio
import datetime

from aiogram import Bot

from core.config import settings
from services.api_client import api_client


def _escape_markdown(text: str) -> str:
    escape_chars = r"_*`[]()"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)


def _formatar_data_br(data_iso: str) -> str:
    try:
        return datetime.date.fromisoformat(data_iso).strftime("%d/%m/%Y")
    except ValueError:
        return data_iso


async def run_expiration_notifier(bot: Bot):
    """
    Loop periódico que busca expirações pendentes do dia e envia
    a notificação automática ao usuário.
    """
    intervalo_segundos = max(settings.EXPIRACAO_CHECK_INTERVAL_MINUTES, 1) * 60

    while True:
        try:
            pendentes = await api_client.get_expiration_pending_notifications()

            for item in pendentes:
                pedido_id = str(item.get("pedido_id"))
                telegram_id = item.get("telegram_id")
                produto_nome = _escape_markdown(item.get("produto_nome", "Produto"))
                data_expiracao = str(item.get("data_expiracao"))
                data_expiracao_br = _formatar_data_br(data_expiracao)

                mensagem = (
                    "⚠️ *Aviso de Expiração*\n\n"
                    f"A sua conta do produto *{produto_nome}* expirou hoje "
                    f"\\({data_expiracao_br}\\)\\.\n\n"
                    "Se precisar, abra um ticket em *🆘 Suporte* "
                    "ou fale diretamente com o administrador\\."
                )

                try:
                    await bot.send_message(chat_id=telegram_id, text=mensagem)
                    await api_client.mark_expiration_notification_sent(pedido_id, data_expiracao)
                except Exception as send_error:
                    print(f"Falha ao enviar notificação de expiração do pedido {pedido_id}: {send_error}")

        except Exception as loop_error:
            print(f"Erro no loop de notificação de expiração: {loop_error}")

        await asyncio.sleep(intervalo_segundos)
