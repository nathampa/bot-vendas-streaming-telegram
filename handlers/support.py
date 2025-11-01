from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from services.api_client import api_client
from states.user_states import SupportStates
from keyboards.inline_keyboards import get_support_orders_keyboard, get_support_reason_keyboard
from keyboards.reply_keyboards import get_main_menu_keyboard

router = Router()

# --- 1. Entrada do Fluxo (Botão "Suporte" ou /suporte) ---

@router.message(F.text == "🆘 Suporte")
@router.message(Command("suporte"))
async def handle_support_start(message: types.Message, state: FSMContext):
    """
    Inicia o fluxo de suporte: busca os pedidos recentes do usuário.
    """
    await state.clear()

    pedidos = await api_client.get_my_orders(telegram_id=message.from_user.id)

    if pedidos is None:
        await message.answer("❌ Não consegui buscar o seu histórico de pedidos. A API pode estar offline.")
        return

    if not pedidos:
        await message.answer("😕 Não encontrei pedidos recentes na sua conta.")
        return

    # Encontrámos pedidos. Mostra-os como botões inline.
    await message.answer(
        "Selecione o pedido com o qual você está a ter problemas:",
        reply_markup=get_support_orders_keyboard(pedidos)
    )

    # Define o estado
    await state.set_state(SupportStates.awaiting_order_selection)

# --- 2. Apanha o clique no botão "Cancelar" (a qualquer momento) ---

@router.callback_query(F.data == "cancel_support", StateFilter("*"))
async def handle_cancel_support(query: types.CallbackQuery, state: FSMContext):
    """
    Cancela o fluxo de suporte.
    """
    await query.answer("Ação cancelada.")
    await query.message.edit_text("Fluxo de suporte cancelado.")
    await state.clear()

# --- 3. Apanha a seleção do Pedido ---

@router.callback_query(F.data.startswith("support_order:"), StateFilter(SupportStates.awaiting_order_selection))
async def handle_order_selection(query: types.CallbackQuery, state: FSMContext):
    """
    Utilizador selecionou um pedido. Agora pergunta o motivo.
    """
    pedido_id = query.data.split(":")[1]

    # Guarda o pedido_id no estado (memória)
    await state.update_data(pedido_id=pedido_id) # <-- Isto está correto

    # Altera a mensagem original (edit_text)
    await query.message.edit_text(
        "Pedido selecionado. Agora, por favor, informe o motivo do problema:",
        reply_markup=get_support_reason_keyboard() # <-- CORRIGIDO (sem argumento)
    )

    # Avança para o próximo estado
    await state.set_state(SupportStates.awaiting_reason)

# --- 4. Apanha a seleção do Motivo (e cria o ticket) ---

@router.callback_query(F.data.startswith("support_reason:"), StateFilter(SupportStates.awaiting_reason))
async def handle_reason_selection(query: types.CallbackQuery, state: FSMContext):
    """
    Utilizador selecionou o motivo. Cria o ticket na API.
    """
    await query.answer("A processar o seu ticket...")

    # 1. Extrai os dados do callback (ex: "support_reason:LOGIN_INVALIDO")
    _, motivo = query.data.split(":")

    # 2. LÊ O PEDIDO_ID DA "MEMÓRIA" DO FSM
    dados_fsm = await state.get_data()
    pedido_id = dados_fsm.get("pedido_id")

    if not pedido_id:
        await query.message.edit_text("❌ Erro de sessão. Por favor, tente o /suporte novamente.")
        await state.clear()
        return

    if motivo == "OUTRO":
        # ... (lógica para "Outro")
        pass

    # 3. Chama a API para criar o ticket (agora com ambos os IDs)
    resultado = await api_client.create_ticket(
        telegram_id=query.from_user.id,
        pedido_id=pedido_id,
        motivo=motivo
    )

    # ... (o resto da lógica de 'if resultado...' continua igual) ...
    if resultado and resultado.get("id"):
        # Sucesso
        await query.message.edit_text(
            "✅ **Ticket aberto com sucesso!**\n\n"
            "A nossa equipa de suporte irá analisar o seu caso."
            " A conta problemática já foi bloqueada."
        )
    elif resultado and resultado.get("detail"):
        # Falha (ex: 409 Ticket já existe)
        await query.message.edit_text(
            f"❌ **Não foi possível abrir o ticket.**\n"
            f"Motivo: {resultado.get('detail')}"
        )
    else:
        # Falha (API offline)
        await query.message.edit_text("❌ Erro de comunicação. Tente novamente mais tarde.")

    await state.clear()