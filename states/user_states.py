from aiogram.fsm.state import State, StatesGroup

class WalletStates(StatesGroup):
    """
    Estados para o fluxo da Carteira (Wallet).
    """
    # Estado: O bot está à espera que o utilizador digite o valor
    # que quer recarregar.
    waiting_for_recharge_amount = State()

# (Aqui adicionaremos mais estados no futuro, ex: SupportStates)