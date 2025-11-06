from aiogram.fsm.state import State, StatesGroup

class WalletStates(StatesGroup):
    """
    Estados para o fluxo da Carteira (Wallet).
    """
    # Estado: O bot está à espera que o utilizador digite o valor
    # que quer recarregar.
    waiting_for_recharge_amount = State()

class SupportStates(StatesGroup):
    """
    Estados para o fluxo de Suporte.
    """
    # 1. Bot está à espera que o user escolha um pedido da lista
    awaiting_order_selection = State()
    # 2. Bot está à espera que o user escolha o motivo do problema
    awaiting_reason = State()

class GiftCardStates(StatesGroup):
    """
    Estados para o fluxo de Resgate de Gift Card.
    """
    # Estado: O bot está à espera que o utilizador digite o código
    waiting_for_code = State()

class SuggestionStates(StatesGroup):
    """
    Estados para o fluxo de Sugestões.
    """
    # Estado: O bot está à espera que o utilizador digite o nome
    awaiting_suggestion = State()

class PurchaseStates(StatesGroup):
    """
    Estados para o fluxo de compra que requer e-mail.
    """
    # 1. Aguardando o usuário digitar o e-mail
    awaiting_email = State()
    # 2. Aguardando o usuário confirmar o e-mail (Sim/Não)
    awaiting_email_confirmation = State()

class BroadcastStates(StatesGroup):
    """
    Estados para o fluxo de Admin Broadcast.
    """
    awaiting_message = State()
    awaiting_confirmation = State()