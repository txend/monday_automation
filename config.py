
from os import environ, path
from decouple import config

try:
    basedir = path.abspath(path.dirname(__file__))
except:
    pass

TEMP_ENV = config('ENV')


class Config:
    """Base config."""
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    pass



class DevConfig(Config):
    ENV = 'development'
    DEBUG = True
    TESTING = True
    GOOGLE_SHEET_KEYS_PATH = config('GOOGLE_SHEET_KEYS_PATH_DEV', cast=str)
    SAMPLE_SPREADSHEET_ID = config('SAMPLE_SPREADSHEET_ID_DEV', cast=str)



class TestConfig(Config):
    ENV = 'testing'
    DEBUG = False
    TESTING = True
    GOOGLE_SHEET_KEYS_PATH = config('GOOGLE_SHEET_KEYS_PATH_TEST', cast=str)
    SAMPLE_SPREADSHEET_ID = config('SAMPLE_SPREADSHEET_ID_TEST', cast=str)


class ProdConfig(Config):
    ENV = 'production'
    DEBUG = False
    TESTING = False
    GOOGLE_SHEET_KEYS_PATH = config('GOOGLE_SHEET_KEYS_PATH_PROD', cast=str)
    SAMPLE_SPREADSHEET_ID = config('SAMPLE_SPREADSHEET_ID_PROD', cast=str)


def get_env():
    if TEMP_ENV == 'development':
        app_config = DevConfig()
        return app_config
    if TEMP_ENV == 'testing':
        app_config = TestConfig()
        return app_config
    if TEMP_ENV == 'production':
        app_config = ProdConfig()
        return app_config