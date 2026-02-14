import logging
import logging.config
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from dotenv import load_dotenv
from app.core.database import Base, engine
from app.api.v1.customer import router as customer_router
from app.api.v1.blacklist import router as blacklist_router
from app.api.v1.fraud_detection import router as fraud_router

load_dotenv()

# Use dictConfig for advanced logging configuration with correlation ID filter
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s [%(correlation_id)s] [%(name)s] %(levelname)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s: %(message)s",
        },
    },
    "filters": {
        "correlation_id": {
            "()": "asgi_correlation_id.CorrelationIdFilter",
            "uuid_length": 32,
            "default_value": "-",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filters": ["correlation_id"],
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filters": ["correlation_id"],
            "filename": "app.log",
            "mode": "a",
        },
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}
logging.config.dictConfig(logging_config)

# Get logger for this module
logger = logging.getLogger(__name__)

app = FastAPI(title="Onboard Customer")
app.add_middleware(CorrelationIdMiddleware)

# Test logging to verify configuration
logger.info("FastAPI application starting up with logging configuration")
logger.debug("Debug logging is enabled")

Base.metadata.create_all(bind=engine)

app.include_router(customer_router)
app.include_router(blacklist_router)
app.include_router(fraud_router)
