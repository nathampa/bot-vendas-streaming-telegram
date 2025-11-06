from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import datetime

# def get_buy_product_keyboard(
#     produto_id: str, 
#     produto_nome: str, 
#     preco: str,
#     requer_email: bool
# ) -> InlineKeyboardMarkup:
#     """
#     Cria um teclado inline "Comprar" (que leva à confirmação).
#     """
#     builder = InlineKeyboardBuilder()
    
#     # O callback data agora é para ABRIR A CONFIRMAÇÃO
#     # E ele precisa carregar o 'requer_email'
#     callback_data = f"confirm_buy:{produto_id}:{requer_email}"
    
#     builder.row(
#         InlineKeyboardButton(
#             text=f"✅ Comprar (R$ {preco})",
#             callback_data=callback_data
#         )
#     )
    
#     return builder.as_markup()

# Função da nova grade de produtos
def build_product_grid(produtos: list) -> InlineKeyboardMarkup:
    """
    Cria um teclado inline com uma grade de botões,
    um para cada produto, em 1 coluna.
    """
    builder = InlineKeyboardBuilder()
    
    for produto in produtos:
        builder.add(
            InlineKeyboardButton(
                # Mostra nome e preço
                text=f"📺 {produto['nome']} (R$ {produto['preco']})",
                # Este callback_data vai acionar a tela de detalhes
                callback_data=f"show_product:{produto['id']}"
            )
        )
    
    # Ajusta para 1 coluna
    builder.adjust(1) 
    return builder.as_markup()

# Função detalhes do pedido
def get_product_details_keyboard(
    produto_id: str, 
    preco: str,
    requer_email: bool
) -> InlineKeyboardMarkup:
    """
    Cria os botões "Comprar" e "Voltar ao Catálogo"
    para a tela de detalhes do produto.
    """
    builder = InlineKeyboardBuilder()

    # Botão 1: Comprar (leva à tela de confirmação existente)
    builder.row(
        InlineKeyboardButton(
            text=f"✅ Comprar (R$ {preco})",
            # Este callback_data aciona o 'handle_show_confirmation'
            # que já existe em purchase.py
            callback_data=f"confirm_buy:{produto_id}:{requer_email}"
        )
    )
    # Botão 2: Voltar
    builder.row(
        InlineKeyboardButton(
            text="« Voltar ao Catálogo",
            # Este callback_data vai nos levar de volta à grade
            callback_data="show_catalog" 
        )
    )
    return builder.as_markup()

def get_purchase_confirmation_keyboard(
    produto_id: str, 
    requer_email: bool
) -> InlineKeyboardMarkup:
    """
    Cria os botões "Confirmar Compra" e "Cancelar".
    """
    builder = InlineKeyboardBuilder()

    # Define o prefixo do callback final (o que costumava ser)
    if requer_email:
        callback_data_prefix = "buy:email:"
    else:
        callback_data_prefix = "buy:auto:"
    
    callback_data = f"{callback_data_prefix}{produto_id}"

    builder.row(
        InlineKeyboardButton(text="✅ Confirmar Compra", callback_data=callback_data)
    )
    builder.row(
        InlineKeyboardButton(
            text="« Cancelar / Voltar", 
            callback_data=f"show_product:{produto_id}"
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
                callback_data=f"support_order:{pedido_id}"
            )
        )

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