from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import datetime

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

def get_support_orders_keyboard(pedidos: list) -> InlineKeyboardMarkup:
    """
    Cria um teclado dinâmico com os últimos 5 pedidos do usuário.
    """
    builder = InlineKeyboardBuilder()

    for pedido in pedidos:
        pedido_id = pedido['pedido_id']
        produto_nome = pedido['produto_nome']
        # Formata a data (ex: 31/10/2025 10:30)
        data = datetime.datetime.fromisoformat(pedido['data_compra']).strftime('%d/%m/%Y %H:%M')

        builder.row(
            InlineKeyboardButton(
                text=f"Pedido: {produto_nome} ({data})",
                # O callback data identifica a ação E o ID do pedido
                callback_data=f"support_order:{pedido_id}"
            )
        )

    builder.row(InlineKeyboardButton(text="« Cancelar", callback_data="cancel_support"))
    return builder.as_markup()

def get_support_reason_keyboard() -> InlineKeyboardMarkup: # <--- REMOVIDO o 'pedido_id' daqui
    """
    Cria um teclado com os motivos do problema.
    O pedido_id NÃO é incluído, pois já está no FSM (memória).
    """
    builder = InlineKeyboardBuilder()

    # O callback data agora é SÓ o motivo
    builder.row(
        InlineKeyboardButton(
            text="Login / Senha Inválida",
            callback_data="support_reason:LOGIN_INVALIDO" # <--- CORRIGIDO
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Conta sem Assinatura",
            callback_data="support_reason:SEM_ASSINATURA" # <--- CORRIGIDO
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Conta Caiu / Parou",
            callback_data="support_reason:CONTA_CAIU" # <--- CORRIGIDO
        )
    )
    builder.row(
        InlineKeyboardButton(text="Outro Motivo", callback_data="support_reason:OUTRO"),
        InlineKeyboardButton(text="« Cancelar", callback_data="cancel_support")
    )
    return builder.as_markup()