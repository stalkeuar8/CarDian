from pydantic_settings import SettingsConfigDict, BaseSettings

class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file='.env', extra='allow')

class DatabaseSettings(Settings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    

class JWTSettings(Settings):
    SECRET_KEY: str
    ACCESS_EXPIRING_TIME_MINS: int
    REFRESH_EXPIRING_TIME_MINS: int
    
    @property
    def SECRETKEY(self) -> str:
        return self.SECRET_KEY

    @property
    def ACC_EXP_TIME(self) -> int:
        return self.ACCESS_EXPIRING_TIME_MINS

    @property
    def REF_EXP_TIME(self) -> int:
        return self.REFRESH_EXPIRING_TIME_MINS


class RedisSettings(Settings):
    REDIS_PORT: int
    REDIS_HOST: str

    @property
    def REDIS_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


class GeminiSettings(Settings):
    GEMINI_API_KEY: str

    @property
    def API_KEY(self) -> str:
        return self.GEMINI_API_KEY


class BotSettings(Settings):
    TG_BOT_KEY: str

    @property
    def BOT_KEY(self) -> str:
        return self.TG_BOT_KEY


database_settings = DatabaseSettings()
jwt_settings = JWTSettings()
redis_settings = RedisSettings()
gemini_settings = GeminiSettings()
bot_settings = BotSettings()