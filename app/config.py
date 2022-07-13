from pydantic import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_username: str
    database_name: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    TESTING = False
    ENV = 'dev'
    DEFAULT_LOCALE = 'en_US'

    DB_NAME = 'auth_service'
    DB_NAME_TEST = f'{DB_NAME}_test'
    DB_NAME_ROOT = 'postgres'
    # DB_CONNECTION: str = "postgresql://postgres:postgres@localhost:5432/"
    # DB_DSN = f'{DB_CONNECTION}{DB_NAME}'
    # DB_DSN_TEST = f'{DB_CONNECTION}{DB_NAME_TEST}'
    # DB_DSN_ROOT = f'{DB_CONNECTION}{DB_NAME_ROOT}'

    # connection timeout and 1/2 of a command timeout
    DB_TIMEOUT: float = 5
    # connection pool settings
    POOL_MIN_SIZE: int = 1
    POOL_MAX_SIZE: int = 20
    POOL_QUERIES: int = 2000
    POOL_LIFETIME: int = 60
    # endregion

    APP_SECRET_KEY: str = 'super_secret'

    HTTPS_PROXY: str = ""

    # CONNECT_URL: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
