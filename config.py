#config.py

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///./test.db"
    TORTOISE_ORM = {
        "connections": {
            "default": SQLALCHEMY_DATABASE_URI
        },
        "apps": {
            "models": {
                "models": ["auth.auth"],
                "default_connection": "default",
            }
        },
        "generate_schemas": True,
        "add_exception_handlers": True,
    }