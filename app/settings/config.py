from pydantic_settings import SettingsConfigDict, BaseSettings

class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file='.env')

class DatabaseSettings(Settings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    

database_settings = DatabaseSettings()