from pydantic import BaseModel, EmailStr
from typing import Optional


class UserInfo(BaseModel):
    username: str
    password: str
    email: EmailStr
    phone: str
    country: str


class EditProfileModel(BaseModel):
    username: str
    password: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    country: Optional[str] = None


class LoginModel(BaseModel):
    email: EmailStr
    password: str


class EditProfileModel(BaseModel):
    field_to_change: str
    new_value: str


class DeckData(BaseModel):
    name: str
    description: str


class GetDeckById(BaseModel):
    id: str


class EditDeckModel(BaseModel):
    id: str
    field_to_change: str
    new_value: str


class DeleteDeckModel(BaseModel):
    id: str


class CardData(BaseModel):
    english_word: str
    translation: str
    explanation: str
    deck_id: str


class GetCardById(BaseModel):
    card_id: str
    deck_id: str


class EditCardModel(BaseModel):
    id: str
    deck: str
    field_to_change: str
    new_value: str


class DeleteCardModel(BaseModel):
    card_id: str
    deck: str


class GetDecksCards(BaseModel):
    deck_id: str


class InterestData(BaseModel):
    name: str


class ID(BaseModel):
    id: str


class PostData(BaseModel):
    text: str


class GroupData(BaseModel):
    name: str
    users: str


class BankCardData(BaseModel):
    number: str
    exp_date: str
    cvv: str


class SocialMediaAccount(BaseModel):
    type: str
    link: str


class GameResults(BaseModel):
    words_learned: int
    decks_learned_fully: int
    decks_learned_partly: int


class Generate(BaseModel):
    id: str
