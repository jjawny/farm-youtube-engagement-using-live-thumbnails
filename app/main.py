from fastapi import FastAPI
from dotenv import load_dotenv
from app.routes import engagement, ping

load_dotenv()

app = FastAPI()
app.include_router(ping.router)
app.include_router(engagement.router)
