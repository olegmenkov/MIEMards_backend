from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate
from loguru import logger


def generate_card_recommendation(topic, existing_words):
    system_prompt = """Based on the provided list of words and topic, suggest a new word and its Russian translation that is contextually relevant to them. Return 2 words with space
    Example 1:
    hammer молоток
    Example 2:
    phone телефон
    """
    user_template = "Given topic {topic} and these words in the card deck: {words}, suggest a new relevant word and its Russian translation."
    words_string = ', '.join(existing_words)
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125")
    chat_template = ChatPromptTemplate.from_messages([SystemMessage(content=system_prompt),
                                                      HumanMessagePromptTemplate.from_template(user_template)])
    formatted_template = chat_template.format_messages(words=words_string, topic=topic)
    message = llm.invoke(formatted_template).content.strip()

    suggested_word_pair = message.split(' ')
    logger.info(suggested_word_pair)
    logger.info('Рекомендация карт сгенерирована!')
    return suggested_word_pair[0], suggested_word_pair[1]
