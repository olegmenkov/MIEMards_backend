from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from db.db_class import Database

from routers import bank_cards, cards, decks, interests, posts, profile, rankings, statistics

from loguru import logger

from database_config import HOST, PORT, USERNAME, PASSWORD, DATABASE

db = Database(HOST, PORT, USERNAME, PASSWORD, DATABASE)
app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router, prefix="/profile", tags=["Profile"])
app.include_router(decks.router, prefix="/decks", tags=["Decks"])
app.include_router(cards.router, prefix="/cards", tags=["Cards"])
app.include_router(interests.router, prefix="/interests", tags=["Interests"])
app.include_router(posts.router, prefix="/posts", tags=["Posts"])
app.include_router(bank_cards.router, prefix="/bank_cards", tags=["Bank cards"])
app.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
app.include_router(rankings.router, prefix="/rankings", tags=["Rankings"])
