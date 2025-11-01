from aiogram import Router, types
from aiogram.filters import CommandStart

# Importa a nossa "ponte" da API
from services.api_client import api_client

# Criamos um "Roteador" para este ficheiro.
# Todos os comandos definidos aqui serão "pendurados" nele.
router = Router()

@router.message(CommandStart())
async def handle_start(message: types.Message):
    """
    Manipulador para o comando /start.
    AGORA TAMBÉM REGISTA O UTILIZADOR NA API.
    """

    nome_utilizador = message.from_user.first_name

    try:
        # 1. Tenta registar/encontrar o utilizador na API
        usuario_api = await api_client.register_user(
            telegram_id=message.from_user.id,
            nome_completo=message.from_user.full_name
        )

        if usuario_api is None:
            # Se o api_client retornou None, a API está offline
            raise Exception("API offline")

        # 2. Se correu bem, cumprimenta e mostra o saldo
        saldo = usuario_api.get("saldo_carteira", "0.00")

        await message.answer(
            f"Olá, {nome_utilizador}! 👋\n"
            f"Bem-vindo ao **Ferreira Streamings**!\n\n"
            f"O seu saldo atual é: **R$ {saldo}**"
        )

        # TODO: Enviar o Menu Principal (com botões)

    except Exception as e:
        # 3. Se falhou (API offline ou outro erro)
        print(f"Erro no /start ao tentar registar usuário: {e}")
        await message.answer(
            "❌ Ups! Estou com dificuldades para me ligar aos nossos servidores agora.\n"
            "A nossa equipa já foi notificada. Por favor, tente novamente mais tarde."
        )