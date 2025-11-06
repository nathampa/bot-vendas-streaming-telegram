import asyncio
from aiogram import Router, types, F, Bot
from aiogram.filters import Command, StateFilter, Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

# Importa nossas configs (para saber quem é o admin)
from core.config import settings
from services.api_client import api_client
from states.user_states import BroadcastStates
from keyboards.inline_keyboards import get_broadcast_confirmation_keyboard
from keyboards.reply_keyboards import get_main_menu_keyboard, get_cancel_keyboard

router = Router()

# --- Filtro de Segurança ---
# Isso garante que SÓ VOCÊ (o admin) pode usar esses comandos
class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == settings.ADMIN_TELEGRAM_ID

# --- 1. Comando /broadcast (Início do fluxo) ---
@router.message(Command("broadcast"), IsAdmin())
async def handle_broadcast_start(message: Message, state: FSMContext):
    """
    [ADMIN] Inicia o fluxo de broadcast.
    """
    await state.clear()
    await state.set_state(BroadcastStates.awaiting_message)
    await message.answer(
        "Ok, admin. Por favor, **encaminhe ou envie** a mensagem "
        "que você deseja transmitir para todos os clientes.\n\n"
        "(Use /cancelar ou o botão abaixo para sair)",
        reply_markup=get_cancel_keyboard()
    )

# --- 2. Comando /cancelar (durante o fluxo) ---
@router.message(Command("cancelar"), IsAdmin(), StateFilter(BroadcastStates))
@router.message(F.text.casefold() == "cancelar", IsAdmin(), StateFilter(BroadcastStates))
async def handle_broadcast_cancel_text(message: Message, state: FSMContext):
    """
    [ADMIN] Cancela o fluxo de broadcast por texto.
    """
    await state.clear()
    await message.answer("Broadcast cancelado.", reply_markup=get_main_menu_keyboard())

# --- 3. Recebimento da Mensagem ---
@router.message(StateFilter(BroadcastStates.awaiting_message), IsAdmin())
async def handle_broadcast_message_received(message: Message, state: FSMContext):
    """
    [ADMIN] Recebe a mensagem a ser copiada.
    """
    # Não podemos salvar o objeto 'message' inteiro no FSM.
    # Salvamos os IDs necessários para copiar a mensagem.
    await state.update_data(
        message_chat_id=message.chat.id,
        message_id=message.message_id
    )
    
    await state.set_state(BroadcastStates.awaiting_confirmation)
    
    # Envia uma prévia (copiando a mensagem de volta para o admin)
    await message.answer(
        "Esta é a mensagem que será enviada. **Confirmar envio?**\n"
        "👇👇👇"
    )
    await message.copy_to(chat_id=message.chat.id)
    
    await message.answer(
        "Tem certeza que deseja enviar esta mensagem para **TODOS** os clientes?\n\n"
        "Esta ação não pode ser desfeita.",
        reply_markup=get_broadcast_confirmation_keyboard()
    )

# --- 4. Confirmação do Envio (Callback) ---
@router.callback_query(F.data == "broadcast:confirm", StateFilter(BroadcastStates.awaiting_confirmation), IsAdmin())
async def handle_broadcast_confirm(query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """
    [ADMIN] O admin clicou em "Sim, enviar". Inicia o envio em massa.
    """
    await query.message.edit_text("Iniciando envio... ⏳")
    
    dados_fsm = await state.get_data()
    msg_chat_id = dados_fsm.get("message_chat_id")
    msg_id = dados_fsm.get("message_id")
    
    if not msg_chat_id or not msg_id:
        await query.message.edit_text("❌ Erro de sessão. Tente /broadcast novamente.")
        await state.clear()
        return

    # 1. Buscar a lista de IDs da API
    user_ids = await api_client.get_all_user_ids()
    
    if user_ids is None:
        await query.message.edit_text("❌ Falha ao buscar lista de usuários na API.")
        await state.clear()
        return
        
    if not user_ids:
        await query.message.edit_text("Nenhum cliente encontrado para enviar.")
        await state.clear()
        return

    # 2. Loop de envio
    sucessos = 0
    falhas = 0
    total = len(user_ids)
    
    await query.message.edit_text(f"Enviando para {total} clientes... (0%)")

    for i, user_id in enumerate(user_ids):
        try:
            # Usamos 'copy_message' para enviar uma cópia limpa
            # (sem o "Encaminhado de...")
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=msg_chat_id,
                message_id=msg_id
            )
            sucessos += 1
        except Exception as e:
            # A falha mais comum é o usuário ter bloqueado o bot
            print(f"Falha ao enviar broadcast para {user_id}: {e}")
            falhas += 1
            
        # Edita a mensagem de status a cada 25 envios
        if (i + 1) % 25 == 0 or (i + 1) == total:
            percentual = int(((i + 1) / total) * 100)
            await query.message.edit_text(
                f"Enviando para {total} clientes... ({percentual}%)\n\n"
                f"Enviados: {sucessos}\n"
                f"Falhas: {falhas}"
            )
        
        # Pausa de segurança para evitar Rate Limit do Telegram
        # (100ms = 10 mensagens por segundo)
        await asyncio.sleep(0.1) 

    # 3. Relatório Final
    await query.message.edit_text(
        f"✅ **Broadcast Concluído!**\n\n"
        f"Enviado com sucesso: {sucessos}\n"
        f"Falhas (bot bloqueado): {falhas}\n"
        f"Total de Clientes: {total}"
    )
    await state.clear()

# --- 5. Cancelamento do Envio (Callback) ---
@router.callback_query(F.data == "broadcast:cancel", StateFilter(BroadcastStates.awaiting_confirmation), IsAdmin())
async def handle_broadcast_cancel_callback(query: types.CallbackQuery, state: FSMContext):
    """
    [ADMIN] O admin clicou em "Cancelar" no teclado inline.
    """
    await state.clear()
    await query.message.edit_text("Broadcast cancelado.")