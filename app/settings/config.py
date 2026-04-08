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
    EXPIRING_TIME_MINS: int

    @property
    def SECRETKEY(self) -> str:
        return self.SECRET_KEY

    @property
    def EXP_TIME(self) -> int:
        return self.EXPIRING_TIME_MINS


class RedisSettings(Settings):
    REDIS_PORT: int
    REDIS_HOST: str

    @property
    def REDIS_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


database_settings = DatabaseSettings()
jwt_settings = JWTSettings()
redis_settings = RedisSettings()