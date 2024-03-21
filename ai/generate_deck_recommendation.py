from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate, ChatPromptTemplate


def generate_deck_recommendation(topic):
    system_prompt = "Generate a list of pairs of words related to the given topic. Each pair should contain an English word and its Russian translation, separated by a comma."
    user_template = "Now, generate pairs of words on the topic: {topic}."

    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125")
    chat_template = ChatPromptTemplate.from_messages([SystemMessage(content=system_prompt),
                                                      HumanMessagePromptTemplate.from_template(user_template)])
    formatted_template = chat_template.format_messages(topic=topic)
    message = llm.invoke(formatted_template).content

    pairs = message.split('\n')
    word_pairs = {pair.split(', ')[0]: pair.split(', ')[1] for pair in pairs if ', ' in pair}
    return word_pairs
