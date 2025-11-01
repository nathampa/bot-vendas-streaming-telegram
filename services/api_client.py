import httpx
from core.config import settings

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

    async def register_user(self, telegram_id: int, nome_completo: str) -> dict | None:
        """
        Regista (ou encontra) um usuário na nossa API.
        (Chama POST /api/v1/usuarios/register)
        """
        
        data = {
            "telegram_id": telegram_id,
            "nome_completo": nome_completo
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
        
        # A nossa API espera um 'float' ou 'Decimal', 
        # garantimos que é float para o JSON
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
                return response.json() # Retorna os dados do PIX (copia_e_cola, qrcode)
            
            except httpx.HTTPStatusError as e:
                print(f"Erro HTTP ao criar recarga: {e.response.status_code} - {e.response.text}")
                return None
            except httpx.RequestError as e:
                print(f"Erro de conexão ao criar recarga: {e}")
                return None

# Criamos uma instância única do cliente para ser usada em todo o bot
api_client = APIClient()