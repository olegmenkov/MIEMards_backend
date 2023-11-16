from pydantic import BaseModel, EmailStr


class RegisterModel(BaseModel):
    username: str
    password: str
    email: EmailStr
    phone: str
    country: str


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
    deck: str


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


class GameResults(BaseModel):
    words_learned: int
    decks_learned_fully: int
    decks_learned_partly: int
