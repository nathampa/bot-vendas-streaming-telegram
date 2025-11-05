from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import datetime

def get_buy_product_keyboard(
    produto_id: str, 
    produto_nome: str, 
    preco: str,
    requer_email: bool
) -> InlineKeyboardMarkup:
    """
    Cria um teclado inline "Comprar".
    O callback_data agora inclui o TIPO de compra.
    """
    builder = InlineKeyboardBuilder()
    
    # Define o prefixo com base no tipo de produto
    if requer_email:
        # Ex: "buy:email:uuid-do-produto"
        callback_data_prefix = "buy:email:"
    else:
        # Ex: "buy:auto:uuid-do-produto"
        callback_data_prefix = "buy:auto:"
        
    callback_data = f"{callback_data_prefix}{produto_id}"
    
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
        InlineKeyboardButton(text="« Cancelar", callback_data="cancel_support"),
        InlineKeyboardButton(
            text="💬 Falar com Admin", 
            url="https://t.me/nathampa"
        )
    )
        
    return builder.as_markup()

def get_support_reason_keyboard() -> InlineKeyboardMarkup:
    """
    Cria um teclado com os motivos do problema.
    O pedido_id NÃO é incluído, pois já está no FSM (memória).
    """
    builder = InlineKeyboardBuilder()

    # O callback data agora é SÓ o motivo
    builder.row(
        InlineKeyboardButton(
            text="Login / Senha Inválida",
            callback_data="support_reason:LOGIN_INVALIDO"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Conta sem Assinatura",
            callback_data="support_reason:SEM_ASSINATURA"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Conta Caiu / Parou",
            callback_data="support_reason:CONTA_CAIU"
        )
    )
    builder.row(
        InlineKeyboardButton(text="Outro Motivo", callback_data="support_reason:OUTRO"),
        InlineKeyboardButton(text="« Cancelar", callback_data="cancel_support")
    )
    return builder.as_markup()

def get_email_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Cria os botões "Sim, está correto" e "Não, digitar novamente".
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Sim, está correto", callback_data="buy_email:confirm"),
        InlineKeyboardButton(text="✏️ Não, digitar novamente", callback_data="buy_email:retry")
    )
    builder.row(
        InlineKeyboardButton(text="« Cancelar Compra", callback_data="buy_email:cancel")
    )
    return builder.as_markup()