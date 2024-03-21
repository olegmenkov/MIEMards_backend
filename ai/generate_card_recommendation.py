from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from loguru import logger


def generate_card_recommendation(topic, existing_words):
    system_prompt = "Based on the provided list of words, suggest a new word and its Russian translation that is contextually relevant to them."
    user_template = "Given these words in the card deck: {words}, and topic {topic} suggest a new relevant word and its Russian translation."
    words_string = ', '.join(existing_words)
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125")
    chat_template = ChatPromptTemplate.from_messages([SystemMessage(content=system_prompt),
                                                      HumanMessagePromptTemplate.from_template(user_template)])
    formatted_template = chat_template.format_messages(words=words_string, topic=topic)
    message = llm.invoke(formatted_template).content.strip()

    suggested_word_pair = message.split('\n')
    word_dict = {}

    if len(suggested_word_pair) == 2:
        english_word = suggested_word_pair[0].split(': ')[1]
        russian_word = suggested_word_pair[1].split(': ')[1].split(' ')[0]
        word_dict[english_word] = russian_word

    logger.info('Рекомендация карт сгенерирована!')
    return list(word_dict.keys())[0], list(word_dict.values())[0]
