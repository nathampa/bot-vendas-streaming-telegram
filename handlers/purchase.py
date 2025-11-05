import re
from aiogram import Router, types, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext

from services.api_client import api_client
from states.user_states import PurchaseStates  # <-- Importa o novo FSM
from keyboards.inline_keyboards import get_email_confirmation_keyboard # <-- Importa novo teclado
from keyboards.reply_keyboards import get_main_menu_keyboard, get_cancel_keyboard

router = Router()

# Regex simples para validar e-mail (só para filtrar lixo)
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

# --- FLUXO 1: Compra Automática (Login/Senha) ---

@router.callback_query(F.data.startswith("buy:auto:"))
async def handle_buy_auto_callback(query: types.CallbackQuery, state: FSMContext):
    """
    Processa o clique no botão "Comprar" para produtos de entrega AUTOMÁTICA.
    """
    await state.clear() # Garante que limpa qualquer FSM
    await query.answer("A processar a sua compra...")
    msg_processando = await query.message.answer("A processar a sua compra... ⏳")

    try:
        produto_id = query.data.split(":")[2] # Pega o ID (buy:auto:ID)
        telegram_id = query.from_user.id

        # Chama a API (sem e-mail)
        resultado = await api_client.make_purchase(telegram_id, produto_id)
        await msg_processando.delete()

        if resultado.get("success"):
            # SUCESSO!
            dados_compra = resultado.get("data", {})
            texto_sucesso = (
                f"✅ **Compra Concluída!**\n\n"
                f"Obrigado por comprar o **{dados_compra.get('produto_nome')}**.\n\n"
                f"{dados_compra.get('mensagem_entrega')}\n" # Mensagem da API
                f"Login: `{dados_compra.get('login')}`\n"
                f"Senha: `{dados_compra.get('senha')}`\n\n"
                f"⚠️ *Por favor, não altere a senha! Apenas 1 utilizador por conta.*\n\n"
                f"O seu novo saldo é: **R$ {dados_compra.get('novo_saldo')}**"
            )
            await query.message.answer(texto_sucesso)
        else:
            # FALHA! (Saldo, Estoque, etc.)
            status_code = resultado.get("status_code")
            detalhe = resultado.get("detail", "Erro desconhecido")
            texto_falha = f"❌ **Falha na Compra**\n\nMotivo: {detalhe}"
            if status_code == 402:
                texto_falha += "\n\nPor favor, vá a '💳 Carteira' para adicionar mais saldo."
            
            await query.message.answer(texto_falha)

    except Exception as e:
        await msg_processando.delete()
        print(f"Erro inesperado no fluxo de compra AUTO: {e}")
        await query.message.answer("❌ Ocorreu um erro crítico. Tente novamente.")


# --- FLUXO 2: Compra Manual (E-mail) ---

@router.callback_query(F.data.startswith("buy:email:"))
async def handle_buy_email_start(query: types.CallbackQuery, state: FSMContext):
    """
    PASSO 1: Inicia o fluxo de compra manual, pedindo o e-mail.
    """
    await query.answer("Este produto requer entrega manual.")
    
    produto_id = query.data.split(":")[2] # Pega o ID (buy:email:ID)

    # Guarda o ID do produto na "memória" (FSM)
    await state.update_data(produto_id=produto_id)
    
    # Pergunta pelo e-mail
    await query.message.answer(
        "Para este produto, precisamos do seu e-mail para onde o convite será enviado.\n\n"
        "Por favor, **digite o seu endereço de e-mail**:\n\n"
        "Use /cancelar ou o botão abaixo para voltar.",
        reply_markup=get_cancel_keyboard()
    )
    
    # Define o próximo estado
    await state.set_state(PurchaseStates.awaiting_email)


@router.message(StateFilter(PurchaseStates.awaiting_email), F.text)
async def handle_email_received(message: types.Message, state: FSMContext):
    """
    PASSO 2: O usuário digitou um e-mail.
    """
    email = message.text.strip()
    
    # Validação simples
    if not re.match(EMAIL_REGEX, email):
        await message.answer(
            "❌ E-mail inválido.\n"
            "Por favor, digite um e-mail válido (ex: `exemplo@gmail.com`):",
            reply_markup=get_cancel_keyboard()
        )
        return # Continua no mesmo estado 'awaiting_email'

    # Guarda o e-mail na memória
    await state.update_data(email_cliente=email)
    
    # Pede confirmação
    await message.answer(
        f"O e-mail `{email}` está correto?",
        reply_markup=get_email_confirmation_keyboard()
    )
    
    # Avança para o estado de confirmação
    await state.set_state(PurchaseStates.awaiting_email_confirmation)


@router.callback_query(F.data == "buy_email:retry", StateFilter(PurchaseStates.awaiting_email_confirmation))
async def handle_email_retry(query: types.CallbackQuery, state: FSMContext):
    """
    PASSO 2.5: O usuário clicou em "Não, digitar novamente".
    """
    await query.answer()
    await query.message.edit_text("Ok. Por favor, digite o seu e-mail novamente:",
                                  reply_markup=get_cancel_keyboard())
    
    # Volta para o estado de esperar o e-mail
    await state.set_state(PurchaseStates.awaiting_email)


@router.callback_query(F.data == "buy_email:confirm", StateFilter(PurchaseStates.awaiting_email_confirmation))
async def handle_email_confirm(query: types.CallbackQuery, state: FSMContext):
    """
    PASSO 3: O usuário confirmou o e-mail. Executa a compra.
    """
    await query.answer("A processar a sua compra...")
    await query.message.edit_text("A processar a sua compra... ⏳") # Edita a mensagem "Está correto?"
    
    dados_fsm = await state.get_data()
    email = dados_fsm.get("email_cliente")
    produto_id = dados_fsm.get("produto_id")
    telegram_id = query.from_user.id
    
    if not email or not produto_id:
        await query.message.edit_text("❌ Erro de sessão. Por favor, comece de novo.")
        await state.clear()
        return

    try:
        # Chama a API (AGORA COM O E-MAIL)
        resultado = await api_client.make_purchase(telegram_id, produto_id, email)

        if resultado.get("success"):
            # SUCESSO!
            dados_compra = resultado.get("data", {})
            texto_sucesso = (
                f"✅ **Compra Concluída!**\n\n"
                f"Obrigado por comprar o **{dados_compra.get('produto_nome')}**.\n\n"
                f"**{dados_compra.get('mensagem_entrega')}**\n\n" # Mensagem da API
                f"O seu novo saldo é: **R$ {dados_compra.get('novo_saldo')}**"
            )
            await query.message.edit_text(texto_sucesso)
        else:
            # FALHA! (Saldo, Estoque, etc.)
            detalhe = resultado.get("detail", "Erro desconhecido")
            await query.message.edit_text(f"❌ **Falha na Compra**\n\nMotivo: {detalhe}")

    except Exception as e:
        print(f"Erro inesperado no fluxo de compra EMAIL: {e}")
        await query.message.edit_text("❌ Ocorreu um erro crítico. Tente novamente.")
    finally:
        await state.clear() # Limpa o FSM


@router.message(Command("cancelar"), StateFilter(PurchaseStates))
@router.message(F.text.casefold() == "cancelar", StateFilter(PurchaseStates))
async def handle_cancel_purchase_command(message: types.Message, state: FSMContext):
    """
    Cancela o fluxo de compra de e-mail (via comando /cancelar ou texto).
    """
    await state.clear()
    await message.answer(
        "Compra cancelada. A voltar ao menu principal.",
        reply_markup=get_main_menu_keyboard()
    )