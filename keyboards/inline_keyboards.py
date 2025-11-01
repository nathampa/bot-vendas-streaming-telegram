from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_buy_product_keyboard(produto_id: str, produto_nome: str, preco: str) -> InlineKeyboardMarkup:
    """
    Cria um teclado inline com um único botão "Comprar" para um produto.
    """
    builder = InlineKeyboardBuilder()
    
    # Criamos um "callback_data" que é um prefixo + o ID do produto.
    # Ex: "buy:ca176f9d-e1f9-426b-ab6f-1d01d6b7edcb"
    # O "buy:" diz-nos que é um botão de compra.
    callback_data = f"buy:{produto_id}"
    
    builder.row(
        InlineKeyboardButton(
            text=f"✅ Comprar (R$ {preco})",
            callback_data=callback_data
        )
    )
    
    return builder.as_markup()