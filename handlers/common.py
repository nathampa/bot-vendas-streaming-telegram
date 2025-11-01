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
    """
    
    # 1. Cumprimenta o utilizador
    nome_utilizador = message.from_user.first_name
    await message.answer(
        f"Olá, {nome_utilizador}! 👋\n"
        f"Bem-vindo ao **Ferreira Streamings**!"
    )
    
    # 2. Testa a ligação com a API (em segundo plano)
    await message.answer("A verificar a ligação com os nossos servidores...")
    
    # 3. Chama o nosso api_client para buscar os produtos
    produtos = await api_client.get_produtos()
    
    if produtos is not None:
        # Sucesso!
        await message.answer(
            f"✅ Ligação bem-sucedida!\n"
            f"Encontrámos {len(produtos)} produtos na nossa loja."
        )
        # (Aqui, no futuro, mostraremos o menu principal)
    else:
        # Falha!
        await message.answer(
            "❌ Ups! Estou com dificuldades para me ligar aos nossos servidores agora.\n"
            "A nossa equipa já foi notificada. Por favor, tente novamente mais tarde."
        )