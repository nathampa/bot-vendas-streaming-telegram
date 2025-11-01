from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Carrega e valida as variáveis de ambiente do bot
    a partir do ficheiro .env
    """
    
    # Token do Bot do Telegram (do @BotFather)
    TELEGRAM_BOT_TOKEN: str
    
    # Chave de API para a nossa API FastAPI
    API_KEY: str
    
    # URL base da nossa API FastAPI
    API_BASE_URL: str

    # Configuração para ler do ficheiro .env
    model_config = SettingsConfigDict(env_file=".env")

# Criamos uma instância única que será importada em todo o projeto do bot
settings = Settings()