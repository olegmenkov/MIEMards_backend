from datetime import datetime

# Для начала используем простой словарь для хранения данных

users_table = {
    "0": {"username": "Vasya", "password": "12345", "email": "vasya@example.com",
          "phone": "88005553535",
          "country": "Russia"},
    "1": {"username": "Masha", "password": "54321", "email": "masha@example.com",
          "phone": "88003335353",
          "country": "Belarus"},
}

decks_table = {
    "0": {
        "id": "d_id1", "creator": "1", "name": "A1", "description": "vocabulary for beginners"
    }
}

cards_table = {
    "0": {
        "deck": "0", "english_word": "peace", "translation": "мир", "explanation": "отсутствие войны"
    },
    "1": {
        "deck": "0", "english_word": "world", "translation": "мир",
        "explanation": "часть вселенной, планета"
    }
}

achievements = {
    "0": {
        datetime.strptime("16.11.2023", "%d.%m.%Y"): {"words_learned": 20, "decks_learned_fully": 5,
                                                      "decks_learned_partly": 7, "games": 7},
        datetime.strptime("14.11.2023", "%d.%m.%Y"): {"words_learned": 15, "decks_learned_fully": 3,
                                                      "decks_learned_partly": 3, "games": 5},
        datetime.strptime("17.10.2023", "%d.%m.%Y"): {"words_learned": 8, "decks_learned_fully": 1,
                                                      "decks_learned_partly": 2, "games": 3}
    }
}
