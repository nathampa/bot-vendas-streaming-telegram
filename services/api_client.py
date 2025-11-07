import httpx
from core.config import settings
from typing import Optional

class APIClient:
    """
    Cliente HTTP assíncrono para comunicar com a nossa API FastAPI.
    Usa 'httpx.AsyncClient' para fazer pedidos não-bloqueantes,
    o que é essencial para o 'aiogram'.
    """
    def __init__(self):
        self.base_url = settings.API_BASE_URL
        
        # Prepara os cabeçalhos que serão usados em todos os pedidos do bot
        self.bot_headers = {
            "X-API-Key": settings.API_KEY, # O nosso "cadeado" de segurança
            "Accept": "application/json"
        }

    async def get_produtos(self) -> list | None:
        """
        Busca a lista de produtos ativos na API.
        (Chama GET /api/v1/produtos/)
        """
        async with httpx.AsyncClient() as client:
            try:
                print("APIClient: A tentar buscar /produtos/")
                response = await client.get(
                    f"{self.base_url}/produtos/",
                    headers=self.bot_headers
                )
                response.raise_for_status() 
                print(f"APIClient: /produtos/ retornado com sucesso ({response.status_code})")
                return response.json()
            
            except httpx.HTTPStatusError as e:
                print(f"Erro HTTP ao buscar produtos: {e.response.status_code} - {e.response.text}")
                return None
            except httpx.RequestError as e:
                print(f"Erro de conexão ao buscar produtos: {e}")
                return None

    async def register_user(self, telegram_id: int, nome_completo: str, referrer_id: Optional[int] = None) -> dict | None:
        """
        Regista (ou encontra) um usuário na nossa API.
        (Chama POST /api/v1/usuarios/register)
        """
        
        data = {
            "telegram_id": telegram_id,
            "nome_completo": nome_completo,
            "referrer_id": referrer_id
        }
        
        async with httpx.AsyncClient() as client:
            try:
                print(f"APIClient: A tentar registar usuário {telegram_id}...")
                response = await client.post(
                    f"{self.base_url}/usuarios/register",
                    json=data,
                    headers=self.bot_headers
                )
                
                response.raise_for_status() 
                
                print(f"APIClient: Usuário {telegram_id} registado/encontrado com sucesso.")
                return response.json() # Retorna os dados do usuário (incluindo saldo)
            
            except httpx.HTTPStatusError as e:
                print(f"Erro HTTP ao registar usuário: {e.response.status_code} - {e.response.text}")
                return None
            except httpx.RequestError as e:
                print(f"Erro de conexão ao registar usuário: {e}")
                return None

    async def create_recharge(
        self, 
        telegram_id: int, 
        nome_completo: str, 
        valor: float
    ) -> dict | None:
        """
        Solicita a criação de um PIX de recarga à API.
        (Chama POST /api/v1/recargas/)
        """
        
        data = {
            "telegram_id": telegram_id,
            "nome_completo": nome_completo,
            "valor": float(valor)
        }
        
        async with httpx.AsyncClient() as client:
            try:
                print(f"APIClient: A tentar criar recarga de {valor} para {telegram_id}...")
                response = await client.post(
                    f"{self.base_url}/recargas/",
                    json=data,
                    headers=self.bot_headers
                )
                
                response.raise_for_status() 
                
                print(f"APIClient: Recarga criada com sucesso.")
                return response.json() # Retorna os dados do PIX
            
            except httpx.HTTPStatusError as e:
                print(f"Erro HTTP ao criar recarga: {e.response.status_code} - {e.response.text}")
                return None
            except httpx.RequestError as e:
                print(f"Erro de conexão ao criar recarga: {e}")
                return None

    async def make_purchase(
        self, 
        telegram_id: int, 
        produto_id: str,
        email_cliente: str | None = None
    ) -> dict:
        """
        Tenta executar uma compra usando o saldo da carteira.
        (Chama POST /api/v1/compras/)
        Retorna um dicionário indicando sucesso ou falha.
        """
        
        data = {
            "telegram_id": telegram_id,
            "produto_id": produto_id
        }
        if email_cliente:
            data["email_cliente"] = email_cliente
        
        async with httpx.AsyncClient() as client:
            try:
                print(f"APIClient: A tentar compra do produto {produto_id} para {telegram_id}...")
                response = await client.post(
                    f"{self.base_url}/compras/",
                    json=data,
                    headers=self.bot_headers
                )
                
                # Se der erro (ex: 402 Saldo, 404 Stock), levanta uma exceção
                response.raise_for_status() 
                
                print(f"APIClient: Compra bem-sucedida.")
                # Retorna os dados da compra (login, senha, novo_saldo, etc.)
                return {"success": True, "data": response.json()}
            
            except httpx.HTTPStatusError as e:
                # A API retornou um erro (ex: 402 Saldo Insuficiente)
                print(f"Erro HTTP ao fazer compra: {e.response.status_code}")
                # Tenta extrair a mensagem de 'detail' da nossa API
                try:
                    error_detail = e.response.json().get("detail", "Erro desconhecido")
                except:
                    error_detail = e.response.text
                return {"success": False, "status_code": e.response.status_code, "detail": error_detail}
            
            except httpx.RequestError as e:
                # A API está offline
                print(f"Erro de conexão ao fazer compra: {e}")
                return {"success": False, "status_code": 503, "detail": "Serviço indisponível (API offline)."}
    
    async def get_my_orders(self, telegram_id: int) -> list | None:
        """
        Busca o histórico de 5 pedidos do usuário na API.
        (Chama GET /api/v1/usuarios/meus-pedidos)
        """
        async with httpx.AsyncClient() as client:
            try:
                print(f"APIClient: A buscar pedidos para {telegram_id}...")
                response = await client.get(
                    f"{self.base_url}/usuarios/meus-pedidos",
                    headers=self.bot_headers,
                    params={"telegram_id": telegram_id} # Envia como ?telegram_id=...
                )
                response.raise_for_status()
                print("APIClient: Pedidos encontrados.")
                return response.json()

            except httpx.HTTPStatusError as e:
                print(f"Erro HTTP ao buscar pedidos: {e.response.status_code} - {e.response.text}")
                return None
            except httpx.RequestError as e:
                print(f"Erro de conexão ao buscar pedidos: {e}")
                return None
    
    async def create_ticket(
    self, 
    telegram_id: int, 
    pedido_id: str, 
    motivo: str
) -> dict | None:
        """
        Cria um novo ticket de suporte.
        (Chama POST /api/v1/tickets/)
        """
        data = {
            "telegram_id": telegram_id,
            "pedido_id": pedido_id,
            "motivo": motivo
        }

        async with httpx.AsyncClient() as client:
            try:
                print(f"APIClient: A tentar criar ticket para pedido {pedido_id}...")
                response = await client.post(
                    f"{self.base_url}/tickets/",
                    json=data,
                    headers=self.bot_headers
                )
                response.raise_for_status()
                print("APIClient: Ticket criado com sucesso.")
                return response.json()

            except httpx.HTTPStatusError as e:
                print(f"Erro HTTP ao criar ticket: {e.response.status_code} - {e.response.text}")
                return e.response.json() # Retorna o erro (ex: 409 "Já existe")
            except httpx.RequestError as e:
                print(f"Erro de conexão ao criar ticket: {e}")
                return None
            
    async def redeem_gift_card(self, telegram_id: int, codigo: str) -> dict:
        """
        Tenta resgatar um gift card usando um código.
        (Chama POST /api/v1/giftcards/resgatar)
        Retorna um dicionário indicando sucesso ou falha.
        """

        data = {
            "telegram_id": telegram_id,
            "codigo": codigo
        }

        async with httpx.AsyncClient() as client:
            try:
                print(f"APIClient: A tentar resgatar código {codigo} para {telegram_id}...")
                response = await client.post(
                    f"{self.base_url}/giftcards/resgatar",
                    json=data,
                    headers=self.bot_headers
                )

                # Se der erro (ex: 404, 410), levanta uma exceção
                response.raise_for_status() 

                print(f"APIClient: Código resgatado com sucesso.")
                # Retorna os dados do resgate (valor, novo_saldo)
                return {"success": True, "data": response.json()}

            except httpx.HTTPStatusError as e:
                # A API retornou um erro (ex: 404 Código não encontrado, 410 Já usado)
                print(f"Erro HTTP ao resgatar código: {e.response.status_code}")
                try:
                    error_detail = e.response.json().get("detail", "Erro desconhecido")
                except:
                    error_detail = e.response.text
                return {"success": False, "status_code": e.response.status_code, "detail": error_detail}

            except httpx.RequestError as e:
                # A API está offline
                print(f"Erro de conexão ao resgatar código: {e}")
                return {"success": False, "status_code": 503, "detail": "Serviço indisponível (API offline)."}
            
    async def create_suggestion(self, telegram_id: int, nome_streaming: str) -> dict | None:
        """
        Envia uma nova sugestão de streaming para a API.
        (Chama POST /api/v1/sugestoes/)
        """

        data = {
            "telegram_id": telegram_id,
            "nome_streaming": nome_streaming
        }

        async with httpx.AsyncClient() as client:
            try:
                print(f"APIClient: A enviar sugestão '{nome_streaming}' para {telegram_id}...")
                response = await client.post(
                    f"{self.base_url}/sugestoes/",
                    json=data,
                    headers=self.bot_headers
                )

                response.raise_for_status() 

                print(f"APIClient: Sugestão enviada com sucesso.")
                return response.json() # Retorna os dados da sugestão

            except httpx.HTTPStatusError as e:
                # Ex: 404 (Usuário não encontrado), 400 (Nome muito curto)
                print(f"Erro HTTP ao enviar sugestão: {e.response.status_code} - {e.response.text}")
                return e.response.json()
            except httpx.RequestError as e:
                # A API está offline
                print(f"Erro de conexão ao enviar sugestão: {e}")
                return None
            
    # Metodo buscar ids de todos usuarios
    async def get_all_user_ids(self) -> list[int] | None:
        """
        Busca a lista de todos os Telegram IDs dos clientes na API.
        (Chama GET /api/v1/usuarios/all-ids)
        """
        async with httpx.AsyncClient() as client:
            try:
                print("APIClient: A tentar buscar /usuarios/all-ids/")
                response = await client.get(
                    f"{self.base_url}/usuarios/all-ids",
                    headers=self.bot_headers
                )
                response.raise_for_status() 
                print(f"APIClient: /usuarios/all-ids/ retornado com sucesso ({response.status_code})")
                return response.json() # Retorna a lista [123, 456, ...]
            
            except httpx.HTTPStatusError as e:
                print(f"Erro HTTP ao buscar IDs de usuários: {e.response.status_code} - {e.response.text}")
                return None
            except httpx.RequestError as e:
                print(f"Erro de conexão ao buscar IDs de usuários: {e}")
                return None

# Criamos uma instância única do cliente para ser usada em todo o bot
api_client = APIClient()