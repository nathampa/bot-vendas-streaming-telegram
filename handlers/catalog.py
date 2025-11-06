from aiogram import Router, types, F
from aiogram.filters import Command

from services.api_client import api_client
from keyboards.inline_keyboards import build_product_grid

router = Router()

@router.message(F.text == "🛍️ Ver Produtos")
@router.message(Command("produtos"))
async def handle_list_products(message: types.Message):
    """
    Busca produtos na API e exibe como uma grade de botões inline.
    """
    await message.answer("Buscando produtos disponíveis... ⏳")
    
    produtos = await api_client.get_produtos()
    
    if not produtos:
        await message.answer(
            "😕 Nenhum produto disponível no momento. "
            "Tente novamente mais tarde."
        )
        return

    # Gera o teclado de grade
    teclado_grid = build_product_grid(produtos)
    
    # Envia UMA ÚNICA mensagem com a grade
    await message.answer(
        "**Nossos Produtos:**\n\n"
        "Selecione um produto abaixo para ver os detalhes e comprar:",
        reply_markup=teclado_grid
    )