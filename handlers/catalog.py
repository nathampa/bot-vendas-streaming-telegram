from aiogram import Router, types, F
from aiogram.filters import Command

from services.api_client import api_client
from keyboards.inline_keyboards import get_buy_product_keyboard # O nosso novo botão

router = Router()

@router.message(F.text == "🛍️ Ver Produtos")
@router.message(Command("produtos"))
async def handle_show_products(message: types.Message):
    """
    Mostra o catálogo de produtos.
    """

    await message.answer("A carregar o nosso catálogo... ⏳")

    produtos = await api_client.get_produtos()

    if produtos is None:
        await message.answer("❌ Ups! Não consegui ligar-me à loja. Tente novamente mais tarde.")
        return

    if not produtos:
        await message.answer("😕 Parece que não temos produtos no stock neste momento. Volte em breve!")
        return

    # Envia uma mensagem separada para cada produto
    await message.answer("Aqui estão os nossos produtos disponíveis:")

    for produto in produtos:
        # Formata a mensagem do produto
        texto_produto = (
            f"📺 **{produto['nome']}**\n"
            f"📝 {produto['descricao']}\n\n"
            f"💰 **Preço: R$ {produto['preco']}**"
        )

        # Cria o botão "Comprar" para este produto específico
        requer_email = produto['requer_email_cliente']

        teclado = get_buy_product_keyboard(
            produto_id=produto['id'],
            produto_nome=produto['nome'],
            preco=produto['preco'],
            requer_email=requer_email
        )

        await message.answer(texto_produto, reply_markup=teclado)