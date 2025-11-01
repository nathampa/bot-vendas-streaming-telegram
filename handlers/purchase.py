from aiogram import Router, types, F

from services.api_client import api_client

router = Router()

# Este filtro "apanha" todos os botões inline
# cujo 'callback_data' começa com "buy:"
@router.callback_query(F.data.startswith("buy:"))
async def handle_buy_callback(query: types.CallbackQuery):
    """
    Processa o clique no botão "Comprar".
    """

    # 1. Responde ao Telegram (para o botão parar de "carregar")
    await query.answer("A processar a sua compra...")

    # 2. Envia uma mensagem de feedback (para o utilizador)
    msg_processando = await query.message.answer("A processar a sua compra... ⏳")

    try:
        # 3. Extrai os dados do botão
        produto_id = query.data.split(":")[1]
        telegram_id = query.from_user.id

        # 4. Chama a API para tentar a compra
        resultado = await api_client.make_purchase(telegram_id, produto_id)

        # 5. Apaga a mensagem "A processar..."
        await msg_processando.delete()

        # 6. Processa o resultado da API
        if resultado.get("success"):
            # SUCESSO!
            dados_compra = resultado.get("data", {})

            texto_sucesso = (
                f"✅ **Compra Concluída!**\n\n"
                f"Obrigado por comprar o **{dados_compra.get('produto_nome')}**.\n\n"
                f"Aqui estão as suas credenciais:\n"
                f"Login: `{dados_compra.get('login')}`\n"
                f"Senha: `{dados_compra.get('senha')}`\n\n"
                f"⚠️ *Por favor, não altere a senha! Apenas 1 utilizador por conta.*\n\n"
                f"O seu novo saldo é: **R$ {dados_compra.get('novo_saldo')}**"
            )
            await query.message.answer(texto_sucesso)

        else:
            # FALHA!
            status_code = resultado.get("status_code")
            detalhe = resultado.get("detail", "Erro desconhecido")

            texto_falha = f"❌ **Falha na Compra**\n\n"

            if status_code == 402:
                texto_falha += f"Motivo: {detalhe}\n\n"
                texto_falha += "Por favor, vá a '💳 Carteira' para adicionar mais saldo."
            elif status_code == 404:
                texto_falha += "Motivo: O stock deste produto esgotou-se no exato momento da sua compra. 😕\n\n"
                texto_falha += "Não se preocupe, o seu saldo não foi debitado."
            else:
                texto_falha += f"Motivo: {detalhe}\nPor favor, tente novamente."

            await query.message.answer(texto_falha)

    except Exception as e:
        await msg_processando.delete()
        print(f"Erro inesperado no fluxo de compra: {e}")
        await query.message.answer("❌ Ocorreu um erro crítico ao processar a sua compra. Tente novamente.")