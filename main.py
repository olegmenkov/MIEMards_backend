from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import ai
from ai.generate_image import generate_image
from ai.generate_translation import generate_translation
from ai.generate_card_recommendation import generate_card_recommendation
from ai.generate_deck_recommendation import generate_deck_recommendation

import db.db_functions as db_functions
import authentification
from db.db_class import Database
from schemas import *

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

router_profile = APIRouter()
router_decks = APIRouter()
router_cards = APIRouter()
router_interests = APIRouter()
router_posts = APIRouter()
# router_groups = APIRouter()
router_bank_cards = APIRouter()
# router_accounts = APIRouter()
router_statistics = APIRouter()
router_rankings = APIRouter()


@router_profile.post("/register")
async def register(request_body: UserInfo):
    """
    Регистрирует в БД нового пользователя со всеми полями, указанными при регистрации
    """
    await db_functions.add_user_to_db(db, request_body.username, request_body.password, request_body.email,
                                      request_body.phone, request_body.country)
    return JSONResponse(content={"message": "User registered successfully"})


@router_profile.post("/login")
async def login(request_body: LoginModel):
    """
    Проверяет, существует ли пользователь с таким логином и паролем. Если да, возвращает токен для дальнейшего доступа
    """

    found_user = await db_functions.find_user_by_login_data(db, request_body.email, request_body.password)
    if not found_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(found_user.u_id)
    user_data = {"username": found_user.u_username,
                 "email": found_user.u_email,
                 "phone": found_user.u_phone,
                 "country": found_user.u_country}

    # Создаем токен
    access_token = authentification.create_access_token(data={"sub": str(user_id)})

    # Возвращаем токен в ответе
    return JSONResponse(content={"access_token": access_token, "token_type": "bearer",
                                 "user_id": user_id,
                                 "username": user_data["username"],
                                 "email": user_data["email"],
                                 "phone": user_data["phone"],
                                 "country": user_data["country"]})


@router_profile.patch("")
async def edit_profile(request_body: EditProfileModel, user_id: str = Depends(authentification.get_current_user)):
    """
    Редактирует указанное поле в профиле пользователя, если такое есть
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request_body.model_dump(exclude_unset=True).items():
        # Проверка существования поля в модели
        if field not in UserInfo.__annotations__:
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

        if value is not None:
            await db_functions.edit_users_profile(db, user_id, field, value)

    return JSONResponse(content={"message": "Profile edited successfully"})


@router_profile.get("")
async def get_user_data(user_id: str = Depends(authentification.get_current_user)):
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = await db_functions.get_userdata_by_id(db, user_id)

    return JSONResponse(content=user_data)


@router_profile.delete("")
async def delete_profile(user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет профиль пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await db_functions.delete_user_from_db(db, user_id)

    return JSONResponse(content={"message": "Profile deleted successfully"})


@router_profile.get("/generate_deck")
async def generate_deck(user_id: str = Depends(authentification.get_current_user)):
    """
    Генерирует колоду для данного пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    ai.generate_deck_recommendation.generate_deck_recommendation(user_id)

    return JSONResponse(content={'message': 'Success!'})


@router_decks.post("")
async def create_deck(deck_data: DeckData, user_id: str = Depends(authentification.get_current_user)):
    """
    Создаёт новую колоду, принадлежащую данному пользователю
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    # Вызываем функцию для добавления колоды в базу данных
    deck_id = await db_functions.add_deck(db, deck_data.name, user_id, deck_data.description)

    return JSONResponse(content={"deck_id": deck_id})


@router_decks.get("/get_deck_by_id")
async def get_deck(deck_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает информацию о колоде по её ID в следующем формате:
    {"creator": "userId", "name": "deckName", "description": "deckDescription"}
    """
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    deck_info = await db_functions.get_deck_by_id(db, deck_id)
    return JSONResponse(content=deck_info)


@router_decks.patch("")
async def edit_deck(request_body: DeckData, deck_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Редактирует указанное поле для колоды, если такое есть
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request_body.model_dump(exclude_unset=True).items():
        # Проверка существования поля в модели
        if field not in DeckData.__annotations__:
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

        if value is not None:
            await db_functions.edit_deck_in_db(db, deck_id, field, value)

    return JSONResponse(content={"message": "Deck edited successfully"})


# Эндпоинт для удаления колоды
@router_decks.delete("")
async def delete_deck(deck_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет колоду
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await db_functions.delete_deck_from_db(db, deck_id)

    return JSONResponse(content={"message": "Deck deleted successfully"})


@router_decks.get("/show_decks_of_user")
async def get_decks(user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает все колоды данного пользователя в таком формате
    {
        "deckId": {
            "creator": "userId", "name": "deckName", "description": "deckDescription"
        },
        "deckId2": {
            "creator": "userId", "name": "deckName2", "description": "deckDescription2"
        },
        ...
     }
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    users_decks = await db_functions.get_users_decks(db, user_id)

    return JSONResponse(content=users_decks)


@router_decks.get("/generate_card")
async def generate_card(deck_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Генерирует карточку для данной колоды
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    ai.generate_card_recommendation.generate_card_recommendation(deck_id)

    return JSONResponse(content={'message': 'Success!'})


@router_cards.post("")
async def create_card(card_data: CardData, user_id: str = Depends(authentification.get_current_user)):
    """
    Создаёт новую карту в колоде пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    # Вызываем функцию для добавления карты в базу данных
    card_id = await db_functions.add_card(db, card_data.english_word, card_data.translation, card_data.explanation,
                                          card_data.deck_id)
    return JSONResponse(content={"card_id": card_id})


@router_cards.get("/get_card_by_id")
async def get_card(card_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает информацию по карточке по её ID в следующем формате
    {"english_word": "englishWord", "translation": "translation", "explanation": "explanation",
                            "deck_id": "deckId"}
    """
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    deck_info = await db_functions.get_card_by_id(db, card_id)
    return JSONResponse(content=deck_info)


@router_cards.patch("")
async def edit_card(card_id: str, request_body: CardData, user_id: str = Depends(authentification.get_current_user)):
    """
    Редактирует поле для карточки в колоде, если такое поле есть
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request_body.model_dump(exclude_unset=True).items():
        # Проверка существования поля в модели
        if field not in CardData.__annotations__ and field != "deck_id":
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

        if value is not None:
            await db_functions.edit_card_in_db(db, card_id, field, value)

    return JSONResponse(content={"message": "Card edited successfully"})


@router_cards.delete("")
async def delete_card(card_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет карточку из колоды пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await db_functions.delete_card_from_db(db, card_id)
    return JSONResponse(content={"message": "Card deleted successfully"})


@router_cards.get("/show_cards_from_deck")
async def get_cards(deck_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает все карты в заданной колоде в формате
    {
        "cardId": {
            "deck": "deckId", "english_word": "englishWord", "translation": "translation", "explanation": "explanation"
        },
        "cardId2": {
            "deck": "deckId2", "english_word": "englishWord2", "translation": "translation2", "explanation": "explanation2"
        },
        ...
    }
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    cards = await db_functions.get_decks_cards(db, deck_id)
    return JSONResponse(content=cards)


@router_cards.get("/generate_image")
async def generate_image(card_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Генерирует изображение для данной карточки
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    ai.generate_image.generate_image(card_id)

    return JSONResponse(content={'message': 'Success!'})


@router_cards.get("/generate_translation")
async def generate_translation(card_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Генерирует перевод для данной карточки
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    ai.generate_translation.generate_translation(card_id)

    return JSONResponse(content={'message': 'Success!'})


@router_interests.post("")
async def create_interest(request_body: InterestData, user_id: str = Depends(authentification.get_current_user)):
    """
    Создаёт новый интерес
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    # Вызываем функцию для добавления колоды в базу данных
    interest_id = await db_functions.add_interest(db, user_id, request_body.name)

    return JSONResponse(content={"interest_id": interest_id})


@router_interests.get("/get_interest_by_id")
async def get_interest(interest_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает интерес по айди
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    interest_info = await db_functions.get_interest(db, interest_id)
    return JSONResponse(content=interest_info)


@router_interests.patch("")
async def edit_interest(request_body: InterestData, interest_id: str,
                        user_id: str = Depends(authentification.get_current_user)):
    """
    Меняет интерес
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request_body.model_dump(exclude_unset=True).items():
        # Проверка существования поля в модели
        if field not in InterestData.__annotations__:
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

        if value is not None:
            await db_functions.edit_interest(db, interest_id, field, value)
    return JSONResponse(content={"message": "Interest edited successfully"})


# Эндпоинт для удаления интереса
@router_interests.delete("")
async def delete_interest(interest_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет интерес
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await db_functions.delete_interest(user_id, interest_id)

    return JSONResponse(content={"message": "Interest deleted successfully"})


@router_interests.get("/show_interests_of_user")
async def get_interests(user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает все интересы данного пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    users_interests = await db_functions.get_interests(db, user_id)

    return JSONResponse(content=users_interests)


@router_posts.post("")
async def create_post(request_body: PostData, user_id: str = Depends(authentification.get_current_user)):
    """
    Создаёт новый пост
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    # Вызываем функцию для добавления колоды в базу данных
    post_id = await db_functions.add_post(db, user_id, request_body.text)

    return JSONResponse(content={"post_id": post_id})


@router_posts.get("/get_post_by_id")
async def get_post(post_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает пост по айди
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    post_info = await db_functions.get_post(db, post_id)
    return JSONResponse(content=post_info)


@router_posts.patch("")
async def edit_post(request_body: PostData, post_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Меняет пост
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request_body.model_dump(exclude_unset=True).items():
        # Проверка существования поля в модели
        if field not in PostData.__annotations__:
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

        if value is not None:
            await db_functions.edit_post(db, post_id, field, value)
    return JSONResponse(content={"message": "Post edited successfully"})


@router_posts.delete("")
async def delete_post(post_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет пост
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await db_functions.delete_post(db, post_id)

    return JSONResponse(content={"message": "post deleted successfully"})


@router_posts.get("/show_posts_of_user")
async def get_posts(user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает все посты данного пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    users_posts = await db_functions.get_posts(db, user_id)

    return JSONResponse(content=users_posts)


'''
@router_groups.post("")
async def create_group(request_body: GroupData, user_id: str = Depends(authentification.get_current_user)):
    """
    Создаёт новую группу
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    # Вызываем функцию для добавления колоды в базу данных
    group_id = await db_functions.add_group(db, user_id, request_body.name, request_body.users)

    return JSONResponse(content={"group_id": group_id})


@router_groups.get("/get_group_by_id")
async def get_group(group_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает группу по айди
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    group_info = await db_functions.get_group(db, group_id)
    return JSONResponse(content=group_info)


@router_groups.patch("")
async def edit_group(request_body: GroupData, group_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Меняет группу
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request_body.model_dump(exclude_unset=True).items():
        # Проверка существования поля в модели
        if field not in GroupData.__annotations__:
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

        if value is not None:
            await db_functions.edit_group(db, group_id, field, value)
    return JSONResponse(content={"message": "group edited successfully"})


@router_groups.delete("")
async def delete_group(group_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет группу
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await db_functions.delete_group(db, group_id)

    return JSONResponse(content={"message": "group deleted successfully"})


@router_groups.get("/show_groups_of_user")
async def get_groups(user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает все группы данного пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    users_groups = await db_functions.get_posts(db, user_id)

    return JSONResponse(content=users_groups)
'''


@router_bank_cards.post("")
async def create_bank_card(request_body: BankCardData, user_id: str = Depends(authentification.get_current_user)):
    """
    Создаёт новую карту
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    # Вызываем функцию для добавления колоды в базу данных
    bank_card_id = await db_functions.add_bank_card(db, user_id, request_body.number, request_body.exp_date,
                                                    request_body.cvv)
    return JSONResponse(content={"bank_card_id": bank_card_id})


@router_bank_cards.get("/get_bank_card_by_id")
async def get_bank_card(bank_card_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает карту по айди
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    bank_card_info = await db_functions.get_bank_card(db, bank_card_id)
    return JSONResponse(content=bank_card_info)


@router_bank_cards.patch("")
async def edit_bank_card(request_body: BankCardData, bank_card_id: str,
                         user_id: str = Depends(authentification.get_current_user)):
    """
    Меняет карту
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request_body.model_dump(exclude_unset=True).items():
        # Проверка существования поля в модели
        if field not in BankCardData.__annotations__:
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

        if value is not None:
            await db_functions.edit_bank_card(db, bank_card_id, field, value)
    return JSONResponse(content={"message": "bank card edited successfully"})


@router_bank_cards.delete("")
async def delete_bank_card(bank_card_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет карту
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await db_functions.delete_bank_card(db, bank_card_id)

    return JSONResponse(content={"message": "bank_card deleted successfully"})


@router_bank_cards.get("/show_bank_cards_of_user")
async def get_bank_cards(user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает все карты данного пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    users_bank_cards = await db_functions.get_bank_cards(db, user_id)

    return JSONResponse(content=users_bank_cards)


'''
@router_accounts.post("")
async def create_account(request_body: SocialMediaAccount, user_id: str = Depends(authentification.get_current_user)):
    """
    Привязывает новый аккаунт в соцсетях
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    SOCIAL_MEDIA_TYPES = {
        "VK",
        "INSTAGRAM",
        "FACEBOOK",
        "TELEGRAM",
        "YOUTUBE",
        "X",
        "WECHAT"
    }

    # Вызываем функцию для добавления аккаунта в базу данных
    if request_body.type in SOCIAL_MEDIA_TYPES:
        account_id = await db_functions.add_account(db, user_id, request_body.type, request_body.link)
        return JSONResponse(content={"account_id": account_id})
    else:
        raise HTTPException(status_code=422, detail="Unsupported social media type")


@router_accounts.get("/get_account_by_id")
async def get_account(account_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает аккаунт по айди
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    account_info = await db_functions.get_account(db, account_id)
    return JSONResponse(content=account_info)


@router_accounts.patch("")
async def edit_account(account_id: str, request_body: SocialMediaAccount, user_id: str = Depends(authentification.get_current_user)):
    """
    Меняет аккаунт
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in request_body.model_dump(exclude_unset=True).items():
        # Проверка существования поля в модели
        if field not in SocialMediaAccount.__annotations__:
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

        if value is not None:
            await db_functions.edit_account(db, account_id, field, value)
    return JSONResponse(content={"message": "account edited successfully"})


@router_accounts.delete("")
async def delete_account(account_id: str, user_id: str = Depends(authentification.get_current_user)):
    """
    Удаляет аккаунт
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await db_functions.delete_account(db, account_id)

    return JSONResponse(content={"message": "account deleted successfully"})


@router_accounts.get("/show_accounts_of_user")
async def get_accounts(user_id: str = Depends(authentification.get_current_user)):
    """
    Возвращает все аккаунты данного пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    users_accounts = await db_functions.get_accounts(db, user_id)

    return JSONResponse(content=users_accounts)
'''


@router_statistics.post("")
async def new_game_results(request_body: GameResults, user_id: str = Depends(authentification.get_current_user)):
    """
    Принимает результаты очередной игры и обновляет таблицу достижений пользователя
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await db_functions.update_achievements(db, user_id, request_body.words_learned, request_body.decks_learned_fully,
                                           request_body.decks_learned_partly)

    return JSONResponse(content={"message": "Updated user's achievements successfully"})


@router_statistics.get("/for_today")
async def statistics_for_today(user_id: str = Depends(authentification.get_current_user)):
    """
    Считает и отправляет статистику успехов пользователя за сегодня
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    stats = await db_functions.calculate_daily_stats(db, user_id)
    total_words, fully_learned_decks, partly_learned_decks, games = [param if param else 0 for param in stats]

    ranking = None
    top_all_today = await db_functions.calculate_daily_rating(db)
    for place_from_0 in range(len(top_all_today)):
        if top_all_today[place_from_0]['user_id'] == user_id:
            ranking = place_from_0 + 1

    return JSONResponse(
        content={"total_words": int(total_words), "ranking": ranking, "fully_learned_decks": int(fully_learned_decks),
                 "partly_learned_decks": int(partly_learned_decks), "games": games})


@router_statistics.get("/for_week")
async def statistics_for_week(user_id: str = Depends(authentification.get_current_user)):
    """
    Считает и отправляет статистику успехов пользователя за неделю
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    stats = await db_functions.calculate_weekly_stats(db, user_id)
    total_words, fully_learned_decks, partly_learned_decks, games = [param if param else 0 for param in stats]

    ranking = None
    top_all_week = await db_functions.calculate_weekly_rating(db)
    for place_from_0 in range(len(top_all_week)):
        if top_all_week[place_from_0]['user_id'] == user_id:
            ranking = place_from_0 + 1

    return JSONResponse(
        content={"total_words": int(total_words), "ranking": ranking, "fully_learned_decks": int(fully_learned_decks),
                 "partly_learned_decks": int(partly_learned_decks), "games": games})


@router_statistics.get("/for_alltime")
async def statistics_for_alltime(user_id: str = Depends(authentification.get_current_user)):
    """
    Считает и отправляет статистику успехов пользователя за сегодня
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    stats = await db_functions.calculate_alltime_stats(db, user_id)
    total_words, fully_learned_decks, partly_learned_decks, games = [param if param else 0 for param in stats]

    ranking = None
    top_all_alltime = await db_functions.calculate_alltime_rating(db)
    for place_from_0 in range(len(top_all_alltime)):
        if top_all_alltime[place_from_0]['user_id'] == user_id:
            ranking = place_from_0 + 1

    return JSONResponse(
        content={"total_words": int(total_words), "ranking": ranking, "fully_learned_decks": int(fully_learned_decks),
                 "partly_learned_decks": int(partly_learned_decks), "games": games})


@router_rankings.get("/for_today")
async def rankings_today(user_id: str = Depends(authentification.get_current_user)):
    """
    Считает и отправляет топ пользователей за сегодня
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    top_all_today = await db_functions.calculate_daily_rating(db)

    return JSONResponse(content=top_all_today)


@router_rankings.get("/for_week")
async def rankings_week(user_id: str = Depends(authentification.get_current_user)):
    """
    Считает и отправляет топ пользователей за неделю
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    top_all_week = await db_functions.calculate_weekly_rating(db)

    return JSONResponse(content=top_all_week)


@router_rankings.get("/for_alltime")
async def rankings_week(user_id: str = Depends(authentification.get_current_user)):
    """
    Считает и отправляет топ пользователей за всё время
    """

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")

    top_all_total = await db_functions.calculate_alltime_rating(db)

    return JSONResponse(content=top_all_total)


app.include_router(router_profile, prefix="/profile", tags=["Profile"])
app.include_router(router_decks, prefix="/decks", tags=["Decks"])
app.include_router(router_cards, prefix="/cards", tags=["Cards"])
app.include_router(router_interests, prefix="/interests", tags=["Interests"])
app.include_router(router_posts, prefix="/posts", tags=["Posts"])
# app.include_router(router_groups, prefix="/groups", tags=["Groups"])
app.include_router(router_bank_cards, prefix="/bank_cards", tags=["Bank cards"])
# app.include_router(router_accounts, prefix="/social_accounts", tags=["Social media accounts"])
app.include_router(router_statistics, prefix="/statistics", tags=["Statistics"])
app.include_router(router_rankings, prefix="/rankings", tags=["Rankings"])
