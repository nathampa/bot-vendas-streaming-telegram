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
        # 'async with' garante que o cliente é fechado corretamente
        async with httpx.AsyncClient() as client:
            try:
                print("APIClient: A tentar buscar /produtos/")
                response = await client.get(
                    f"{self.base_url}/produtos/",
                    headers=self.bot_headers
                )
                
                # Levanta um erro se a API retornar 4xx ou 5xx
                response.raise_for_status() 
                
                print(f"APIClient: /produtos/ retornado com sucesso ({response.status_code})")
                return response.json() # Retorna a lista de produtos
            
            except httpx.HTTPStatusError as e:
                # Ex: 401 (API Key errada), 404, 500 (API quebrou)
                print(f"Erro HTTP ao buscar produtos: {e.response.status_code} - {e.response.text}")
                return None
            except httpx.RequestError as e:
                # Ex: A API (Uvicorn) não está a correr
                print(f"Erro de conexão ao buscar produtos: {e}")
                return None

    # (Iremos adicionar mais métodos aqui: criar_recarga, fazer_compra, etc.)

# Criamos uma instância única do cliente para ser usada em todo o bot
api_client = APIClient()