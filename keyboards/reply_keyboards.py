from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Cria e retorna o teclado (botões) do menu principal.
    """
    # Usamos o KeyboardBuilder para criar os botões
    builder = ReplyKeyboardBuilder()
    
    # Adicionamos os botões. 
    # O .add() tenta organizar, .row() força uma nova linha.
    builder.row(
        KeyboardButton(text="🛍️ Ver Produtos"),
        KeyboardButton(text="💳 Carteira")
    )
    builder.row(
        KeyboardButton(text="🎁 Resgatar Código"),
        KeyboardButton(text="🆘 Suporte")
    )
    
    # Converte o builder para um Markup final
    return builder.as_markup(
        resize_keyboard=True, # Faz o teclado adaptar-se ao ecrã
        input_field_placeholder="Use o menu para navegar..."
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    Cria e retorna um teclado simples com um botão "Cancelar".
    """
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="Cancelar"))
    
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Digite uma opção ou cancele a operação..."
    )