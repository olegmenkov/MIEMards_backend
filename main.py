from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse

import db.db_functions as db_functions
import authentification
from schemas import *
from ai import generate_image, generate_translation, generate_card_recommendation, generate_deck_recommendation


# TODO: протестить

app = FastAPI()


# Эндпоинт для регистрации пользователя
@app.post("/register")
async def register(request_body: RegisterModel):
    db_functions.add_user_to_db(request_body.username, request_body.password, request_body.email,
                                request_body.phone, request_body.country)
    return {"message": "User registered successfully"}


# Эндпоинт для входа пользователя
@app.post("/login")
async def login(request_body: LoginModel):
    found_user = db_functions.find_user_by_login_data(request_body.email, request_body.password)
    if not found_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Создаем токен
    access_token = authentification.create_access_token(data={"sub": str(found_user)})

    # Возвращаем токен в ответе
    return {"access_token": access_token, "token_type": "bearer"}


# Эндпоинт для редактирования профиля
@app.put("/edit_profile")
async def edit_profile(request_body: EditProfileModel, user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    if request_body.field_to_change in ["username", "password", "email", "phone", "country"]:
        db_functions.edit_users_profile(user_id, request_body.field_to_change, request_body.new_value)


# Эндпоинт для удаления профиля
@app.delete("/delete_profile")
async def delete_profile(user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    db_functions.delete_user_from_db(user_id)


# Эндпоинт для создания колоды
@app.post("/decks/add")
async def create_deck(deck_data: DeckData, user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    # Вызываем функцию для добавления колоды в базу данных
    deck_id = db_functions.add_deck(deck_data.name, user_id, deck_data.description)

    return JSONResponse(content={"deck_id": deck_id})


@app.get("/decks/get")
async def get_deck(request_body: GetDeckById, user_id: str = Depends(authentification.get_current_user)):
    deck_info = db_functions.get_deck_by_id(request_body.id, user_id)
    return JSONResponse(content=deck_info)


# Эндпоинт для редактирования колоды
@app.put("/decks/edit")
async def edit_deck(request_body: EditDeckModel, user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    if request_body.field_to_change in ["name", "description"]:
        db_functions.edit_deck_in_db(user_id, request_body.id, request_body.field_to_change, request_body.new_value)

    return {"message": "Deck edited successfully"}


# Эндпоинт для удаления колоды
@app.delete("/decks/remove")
async def delete_deck(request_body: DeleteDeckModel, user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    db_functions.delete_deck_from_db(user_id, request_body.id)
    return {"message": "Deck deleted successfully"}


# Эндпоинт для возвращения колод пользователя
@app.get("/decks/show_users_decks")
async def get_decks(user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    users_decks = db_functions.get_users_decks(user_id)

    return JSONResponse(content=users_decks)


# Эндпоинт для создания карты
@app.post("/cards/add")
async def create_card(card_data: CardData, user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    # Вызываем функцию для добавления карты в базу данных
    card_id = db_functions.add_card(card_data.english_word, card_data.translation, card_data.explanation,
                                    card_data.deck_id, user_id)
    return JSONResponse(content={"deck_id": card_id})


@app.get("/cards/get")
async def get_deck(request_body: GetCardById, user_id: str = Depends(authentification.get_current_user)):
    deck_info = db_functions.get_card_by_id(request_body.card_id, request_body.deck, user_id)
    return JSONResponse(content=deck_info)


# Эндпоинт для редактирования карты
@app.put("/cards/edit")
async def edit_card(request_body: EditCardModel, user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    if request_body.field_to_change in ["english_word", "translation", "explanation"]:
        db_functions.edit_card_in_db(user_id, request_body.deck, request_body.id, request_body.field_to_change,
                                     request_body.new_value)

    return {"message": "Card edited successfully"}


# Эндпоинт для удаления карты
@app.delete("/cards/remove")
async def delete_card(request_body: DeleteCardModel, user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    db_functions.delete_card_from_db(user_id, request_body.deck, request_body.card_id)
    return {"message": "Card deleted successfully"}


# Эндпоинт для возвращения карт в колоде
@app.get("/cards/show_decks_cards")
async def get_cards(request_body: GetDecksCards, user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    cards = db_functions.get_decks_cards(user_id, request_body.deck_id)

    return JSONResponse(content=cards)


@app.post("/statistics/new_game_results")
async def new_game_results(request_body: GameResults, user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    db_functions.update_achievements(user_id, request_body.words_learned, request_body.decks_learned_fully,
                                     request_body.decks_learned_partly)

    return {"message": "Updated user's achievements successfully"}


@app.get("/statistics/for_today")
async def statistics_for_today(user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    total_words, fully_learned_decks, partly_learned_decks, total_games = db_functions.get_results_for_today(user_id)
    ranking = db_functions.get_user_rank_for_day(user_id)

    return JSONResponse(
        content={"total_words": total_words, "ranking": ranking, "fully_learned_decks": fully_learned_decks,
                 "partly_learned_decks": partly_learned_decks, "games": total_games})


@app.get("/statistics/for_week")
async def statistics_for_week(user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    total_words, fully_learned_decks, partly_learned_decks, total_games = db_functions.get_weekly_results(user_id)

    ranking = db_functions.get_user_rank_for_week(user_id)

    return JSONResponse(
        content={"total_words": total_words, "ranking": ranking, "fully_learned_decks": fully_learned_decks,
                 "partly_learned_decks": partly_learned_decks, "games": total_games})


@app.get("/statistics/for_alltime")
async def statistics_alltime(user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    total_words, fully_learned_decks, partly_learned_decks, total_games = db_functions.get_total_results(user_id)
    ranking = db_functions.get_user_rank_for_total(user_id)

    return JSONResponse(
        content={"total_words": total_words, "ranking": ranking, "fully_learned_decks": fully_learned_decks,
                 "partly_learned_decks": partly_learned_decks, "games": total_games})


@app.get("/rankings/for_today")
async def rankings_today(user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    content = []  # упорядоченный список
    top_all_today = db_functions.get_top_all_for_day()
    for user_id, words_learned in top_all_today:
        username = db_functions.get_username_by_id(user_id)
        content.append({"username": username, "words learned": words_learned})


@app.get("/rankings/for_week")
async def rankings_week(user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    content = []  # упорядоченный список
    top_all_week = db_functions.get_top_all_for_week()
    for user_id, words_learned in top_all_week:
        username = db_functions.get_username_by_id(user_id)
        content.append({"username": username, "words learned": words_learned})


@app.get("/rankings/for_alltime")
async def rankings_week(user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    content = []  # упорядоченный список
    top_all_total = db_functions.get_top_all_for_total()
    for user_id, words_learned in top_all_total:
        username = db_functions.get_username_by_id(user_id)
        content.append({"username": username, "words learned": words_learned})


@app.get("/generate/card")
async def generate_card(request_body: Generate, user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    ai.generate_card_recommendation.generate_card_recommendation(request_body.id)

    return {'message': 'Success!'}


@app.get("/generate/deck")
async def generate_deck(request_body: Generate, user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    ai.generate_deck_recommendation.generate_deck_recommendation(request_body.id)

    return {'message': 'Success!'}


@app.get("/generate/image")
async def generate_image(request_body: Generate, user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    ai.generate_image.generate_image(request_body.id)

    return {'message': 'Success!'}


@app.get("/generate/translation")
async def generate_translation(request_body: Generate, user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    ai.generate_translation.generate_translation(request_body.id)

    return {'message': 'Success!'}
