from aiogram import Router, types
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from typing import Optional

# Importa a nossa "ponte" da API
from services.api_client import api_client
# Importa o nosso novo teclado
from keyboards.reply_keyboards import get_main_menu_keyboard

# Criamos um "Roteador" para este ficheiro.
router = Router()

@router.message(CommandStart())
async def handle_start(message: types.Message, command: CommandObject, state: FSMContext):
    """
    Manipulador para o comando /start.
    AGORA TAMBÉM REGISTA O UTILIZADOR NA API E CAPTURA O REFERRER.
    """
    await state.clear() # Limpa qualquer estado antigo

    nome_utilizador = message.from_user.first_name
    telegram_id = message.from_user.id
    nome_completo = message.from_user.full_name
    
    referrer_id: Optional[int] = None
    
    # Verifica se há um payload no comando (ex: /start ref_123456)
    if command.args:
        payload = command.args
        if payload.startswith("ref_"):
            try:
                # Extrai o ID do indicador
                ref_id_str = payload.split('_')[-1]
                ref_id_int = int(ref_id_str)
                
                # Usuário não pode indicar a si mesmo
                if ref_id_int != telegram_id:
                    referrer_id = ref_id_int
                    print(f"Novo usuário {telegram_id} foi indicado por {referrer_id}")
                
            except ValueError:
                print(f"Payload de indicação inválido: {payload}")
                
    try:
        # 1. Tenta registar/encontrar o utilizador na API
        usuario_api = await api_client.register_user(
            telegram_id=telegram_id,
            nome_completo=nome_completo,
            referrer_id=referrer_id # <-- Envia o novo ID (ou None)
        )

        if usuario_api is None:
            # Se o api_client retornou None, a API está offline
            raise Exception("API offline")

        # 2. Se correu bem, cumprimenta e mostra o saldo
        saldo = usuario_api.get("saldo_carteira", "0.00")

        texto_boas_vindas = (
            f"Olá, {nome_utilizador}! 👋\n"
            f"Bem-vindo ao **Ferreira Streamings**!\n\n"
            f"O seu saldo atual é: **R$ {saldo}**"
        )
        
        # Se ele foi indicado, manda uma mensagem de agradecimento
        if referrer_id:
             texto_boas_vindas += "\n\nObrigado por se registrar através de um convite!"

        await message.answer(
            texto_boas_vindas,
            reply_markup=get_main_menu_keyboard()
        )

    except Exception as e:
        # 3. Se falhou (API offline ou outro erro)
        print(f"Erro no /start ao tentar registar usuário: {e}")
        await message.answer(
            "❌ Ups! Estou com dificuldades para me ligar aos nossos servidores agora.\n"
            "A nossa equipa já foi notificada. Por favor, tente novamente mais tarde."
        )