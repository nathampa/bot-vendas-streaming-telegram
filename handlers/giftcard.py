from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from services.api_client import api_client
from states.user_states import GiftCardStates # O nosso FSM
from keyboards.reply_keyboards import get_main_menu_keyboard # O menu principal

router = Router()

# --- 1. Manipulador para o botão "Resgatar Código" (ou comando /resgatar) ---

@router.message(F.text == "🎁 Resgatar Código")
@router.message(Command("resgatar"))
async def handle_redeem_start(message: types.Message, state: FSMContext):
    """
    Inicia o fluxo de resgate de gift card.
    """
    await state.clear() # Limpa qualquer estado antigo

    await message.answer(
        "Por favor, digite o seu código de Gift Card:"
    )

    # Define o próximo estado do utilizador
    await state.set_state(GiftCardStates.waiting_for_code)

# --- 2. Manipulador que recebe o código (quando no estado correto) ---

@router.message(StateFilter(GiftCardStates.waiting_for_code), F.text)
async def handle_code_received(message: types.Message, state: FSMContext):
    """
    Recebe o código que o utilizador digitou.
    """

    # Normaliza o código (remove espaços, põe em maiúsculas)
    codigo = message.text.strip().upper()

    await message.answer(f"A verificar o código `{codigo}`... ⏳")

    # Chama a API para tentar o resgate
    resultado = await api_client.redeem_gift_card(
        telegram_id=message.from_user.id,
        codigo=codigo
    )

    # Limpa o estado, quer tenha funcionado ou não
    await state.clear()

    if resultado.get("success"):
        # SUCESSO!
        dados = resultado.get("data", {})
        valor = dados.get('valor_resgatado', '0.00')
        novo_saldo = dados.get('novo_saldo_total', '0.00')

        await message.answer(
            f"✅ **Código resgatado com sucesso!**\n\n"
            f"Valor creditado: **R$ {valor}**\n"
            f"O seu novo saldo é: **R$ {novo_saldo}**",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        # FALHA!
        detalhe = resultado.get("detail", "Erro desconhecido")
        await message.answer(
            f"❌ **Falha ao resgatar o código.**\n"
            f"Motivo: {detalhe}",
            reply_markup=get_main_menu_keyboard()
        )