import datetime

from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from services.api_client import api_client
from states.user_states import SupportStates
from keyboards.inline_keyboards import get_support_orders_keyboard, get_support_reason_keyboard
from keyboards.reply_keyboards import get_main_menu_keyboard
from core.config import settings

router = Router()

def escape_markdown(text: str) -> str:
    escape_chars = r"_*`[]()"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)

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

    expiracao_por_pedido = {
        str(pedido["pedido_id"]): {
            "conta_expirada": bool(pedido.get("conta_expirada", False)),
            "data_expiracao": pedido.get("data_expiracao"),
        }
        for pedido in pedidos
    }
    await state.update_data(expiracao_por_pedido=expiracao_por_pedido)

    teclado_suporte = get_support_orders_keyboard(pedidos)

    if not pedidos:
        # Se não há pedidos, envia uma mensagem explicando
        # e mostra o teclado de admin/cancelar
        texto_sem_pedidos = (
            "😕 Não encontrei pedidos recentes na sua conta.\n\n"
            "Se o seu problema for relacionado a um pedido antigo ou "
            "outro assunto (dúvidas, recargas, etc.), "
            "**fale diretamente com o administrador:**"
        )
        await message.answer(
            texto_sem_pedidos,
            reply_markup=teclado_suporte
        )
        
    else:
        # Se encontrou pedidos, mostra a lista
        await message.answer(
            "Selecione o pedido com o qual você está tendo problemas:",
            reply_markup=teclado_suporte
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
    await state.update_data(pedido_id=pedido_id)

    dados_fsm = await state.get_data()
    expiracao_por_pedido = dados_fsm.get("expiracao_por_pedido", {})
    dados_expiracao = expiracao_por_pedido.get(pedido_id, {})

    aviso_expiracao = ""
    if dados_expiracao.get("conta_expirada"):
        data_expiracao_raw = dados_expiracao.get("data_expiracao")
        data_expiracao_formatada = "data não informada"
        if data_expiracao_raw:
            try:
                data_expiracao_formatada = datetime.date.fromisoformat(data_expiracao_raw).strftime("%d/%m/%Y")
            except ValueError:
                data_expiracao_formatada = str(data_expiracao_raw)

        aviso_expiracao = (
            f"⚠️ Aviso: a conta deste pedido expirou em {data_expiracao_formatada}.\n\n"
        )

    # Altera a mensagem original (edit_text)
    await query.message.edit_text(
        f"{aviso_expiracao}Pedido selecionado. Agora, por favor, informe o motivo do problema:",
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

    texto_resposta = ""
    
    if resultado and resultado.get("id"):
        # Sucesso
        texto_resposta = (
            "✅ **Ticket aberto com sucesso!**\n\n"
            "A nossa equipe de suporte irá analisar o seu caso."
            " A conta problemática já foi bloqueada.\n\n"
            "Se a resolução automática falhar ou demorar, "
            "você pode [falar com o admin](https://t.me/nathampa) a qualquer momento."
        )

        # NOTIFICA O ADMIN SOBRE UM TICKET ABERTO
        try:
            admin_id = settings.ADMIN_TELEGRAM_ID
            user_name = escape_markdown(query.from_user.full_name)
            user_id = escape_markdown(str(query.from_user.id))
            ticket_id = escape_markdown(str(resultado.get('id')))
            pedido_id_md = escape_markdown(str(pedido_id))
            motivo_md = escape_markdown(motivo)
            
            texto_notificacao = (
                f"🔔 **Novo Ticket de Suporte Aberto** 🔔\n\n"
                f"**Cliente:** {user_name} (ID: {user_id})\n"
                f"**Ticket ID:** {ticket_id}\n"
                f"**Pedido ID:** {pedido_id_md}\n"
                f"**Motivo:** {motivo_md}\n\n"
                f"Por favor, verifique o painel admin."
            )
            await query.bot.send_message(chat_id=admin_id, text=texto_notificacao)
        except Exception as e_notify:
            print(f"ERRO AO NOTIFICAR ADMIN (Novo Ticket): {e_notify}")

        
    elif resultado and resultado.get("detail"):
        # Falha (ex: 409 Ticket já existe)
        texto_resposta = (
            f"❌ **Não foi possível abrir o ticket.**\n"
            f"Motivo: {resultado.get('detail')}\n\n"
            "Se precisar de ajuda, [fale com o admin](https://t.me/nathampa)."
        )
    else:
        # Falha (API offline)
        texto_resposta = (
            "❌ Erro de comunicação. Tente novamente mais tarde ou "
            "[fale com o admin](https://t.me/nathampa)."
        )

    await query.message.edit_text(
        texto_resposta,
        disable_web_page_preview=True # Para não mostrar preview do link do Telegram
    )
    await state.clear()
