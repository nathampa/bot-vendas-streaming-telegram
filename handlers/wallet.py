import base64
from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from services.api_client import api_client
from states.user_states import WalletStates # O nosso FSM
from keyboards.reply_keyboards import get_main_menu_keyboard # O menu principal

router = Router()

# --- 1. Manipulador para o botão "Carteira" (ou comando /carteira) ---

@router.message(F.text == "💳 Carteira")
@router.message(Command("carteira"))
async def handle_wallet_menu(message: types.Message, state: FSMContext):
    """
    Mostra o menu da carteira e pergunta quanto adicionar.
    """
    await state.clear() # Limpa qualquer estado antigo

    # TODO: No futuro, este comando deve primeiro buscar o saldo atual na API

    await message.answer(
        "Quanto gostaria de adicionar à sua carteira?\n\n"
        "Por favor, digite um valor (ex: `20.00` ou `20`)."
    )

    # Define o próximo estado do utilizador
    await state.set_state(WalletStates.waiting_for_recharge_amount)

# --- 2. Manipulador que recebe o valor (quando no estado correto) ---

@router.message(StateFilter(WalletStates.waiting_for_recharge_amount), F.text)
async def handle_recharge_amount(message: types.Message, state: FSMContext):
    """
    Recebe o valor que o utilizador digitou.
    """

    # 1. Tenta validar se o que o utilizador digitou é um número
    try:
        valor = float(message.text.replace(",", "."))
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")
    except ValueError:
        await message.answer(
            "❌ Valor inválido!\n"
            "Por favor, digite apenas um número (ex: `20` ou `15.50`)."
        )
        # Mantém o utilizador no mesmo estado, à espera de um valor válido
        return

    # 2. Se o valor for válido, chama a API
    await message.answer("A gerar o seu PIX... ⏳")

    try:
        pix_data = await api_client.create_recharge(
            telegram_id=message.from_user.id,
            nome_completo=message.from_user.full_name,
            valor=valor
        )

        if pix_data is None:
            raise Exception("API falhou ao gerar PIX.")

        # 3. Sucesso! Extrai os dados do PIX (que a API simulou)
        pix_copia_e_cola = pix_data.get("pix_copia_e_cola")
        pix_qr_code_base64 = pix_data.get("pix_qr_code_base64")

        # 4. Limpa o estado
        await state.clear()

        # 5. Envia o PIX (QR Code + Texto)
        # Precisamos de descodificar o QR Code base64
        try:
            # Remove o prefixo "data:image/png;base64,"
            image_data = pix_qr_code_base64.split(",")[1]
            image_bytes = base64.b64decode(image_data)

            # Envia como um ficheiro de foto
            qr_code_file = types.BufferedInputFile(image_bytes, filename="qrcode.png")

            await message.answer_photo(
                photo=qr_code_file,
                caption=(
                    f"✅ PIX gerado com sucesso no valor de **R$ {valor:.2f}**!\n\n"
                    f"Copie o código abaixo e pague no seu banco:\n\n"
                    f"`{pix_copia_e_cola}`\n\n"
                    f"O saldo será creditado automaticamente após o pagamento."
                ),
                # Envia o menu principal de volta
                reply_markup=get_main_menu_keyboard() 
            )

        except Exception as e_img:
            print(f"Erro ao descodificar/enviar QR Code: {e_img}")
            # Plano B: Se o QR Code falhar, envia só o texto
            await message.answer(
                f"✅ PIX gerado com sucesso no valor de **R$ {valor:.2f}**!\n\n"
                f"Copie o código abaixo e pague no seu banco:\n\n"
                f"`{pix_copia_e_cola}`\n\n"
                f"O saldo será creditado automaticamente após o pagamento.",
                reply_markup=get_main_menu_keyboard()
            )

    except Exception as e:
        print(f"Erro ao chamar api_client.create_recharge: {e}")
        await state.clear()
        await message.answer(
            "❌ Ups! Não consegui gerar o seu PIX agora.\n"
            "Por favor, tente novamente mais tarde.",
            reply_markup=get_main_menu_keyboard()
        )