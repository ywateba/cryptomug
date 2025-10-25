from fastapi import FastAPI
import logging

from api.db import models
from api.db.database import engine
from api.config import setup_logging
from api.routers import providers, tokens, prices # Assuming these are now in a 'routers' sub-directory

# Setup logging configuration
setup_logging()
logger = logging.getLogger("CryptoMugAPI")

# This creates the database tables if they don't exist.
# In a production setup with migrations (like Alembic), you might manage this differently.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CryptoMug API",
    description="API for managing cryptocurrency data providers and tokens.",
    version="1.0.0",
)

app.include_router(providers.router)
app.include_router(tokens.router)
app.include_router(prices.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
