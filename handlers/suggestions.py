from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from services.api_client import api_client
from states.user_states import SuggestionStates # O nosso FSM
from keyboards.reply_keyboards import get_main_menu_keyboard, get_cancel_keyboard

router = Router()

# --- 1. Manipulador para o comando /sugerir ---

@router.message(Command("sugerir"))
async def handle_suggest_start(message: types.Message, state: FSMContext):
    """
    Inicia o fluxo de sugestão.
    """
    await state.clear() # Limpa qualquer estado antigo

    await message.answer(
        "Qual serviço de streaming você gostaria que "
        "o **Ferreira Streamings** adicionasse à loja?\n\n"
        "(Use /cancelar ou o botão abaixo para sair)",
        reply_markup=get_cancel_keyboard()
    )

    # Define o próximo estado do utilizador
    await state.set_state(SuggestionStates.awaiting_suggestion)

# --- 2. Manipulador para /cancelar (a meio do fluxo) ---

@router.message(Command("cancelar"), StateFilter(SuggestionStates.awaiting_suggestion))
@router.message(F.text.casefold() == "cancelar", StateFilter(SuggestionStates.awaiting_suggestion)) # <-- MUDANÇA
async def handle_cancel_suggestion(message: types.Message, state: FSMContext):
    """
    Cancela o fluxo de sugestão.
    """
    await state.clear()
    await message.answer(
        "Ação cancelada. A voltar ao menu principal.",
        reply_markup=get_main_menu_keyboard()
    )

# --- 3. Manipulador que recebe a sugestão (quando no estado correto) ---

@router.message(StateFilter(SuggestionStates.awaiting_suggestion), F.text)
async def handle_suggestion_received(message: types.Message, state: FSMContext):
    """
    Recebe o texto da sugestão que o utilizador digitou.
    """

    sugestao_texto = message.text.strip()

    await message.answer(f"A enviar a sua sugestão: '{sugestao_texto}'... ⏳")

    # Chama a API para registar a sugestão
    resultado = await api_client.create_suggestion(
        telegram_id=message.from_user.id,
        nome_streaming=sugestao_texto
    )

    # Limpa o estado, quer tenha funcionado ou não
    await state.clear()

    if resultado and resultado.get("id"):
        # SUCESSO!
        await message.answer(
            f"✅ **Obrigado!**\n\n"
            f"A sua sugestão para '{sugestao_texto}' foi registrada com sucesso.",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        # FALHA!
        detalhe = resultado.get("detail", "Erro desconhecido")
        await message.answer(
            f"❌ **Falha ao enviar a sugestão.**\n"
            f"Motivo: {detalhe}",
            reply_markup=get_main_menu_keyboard()
        )