import os
from dotenv import load_dotenv; load_dotenv()
from app.connection.openai_connection import MyOAI

GET_INTENT_PROMPT = """
You are an master in understanding and summarizing. Depend on the user questions, classify these questions into some categories given below.
Note that: The user's background is engineering in oil and gas exploration and production.
Categories:
- "basic": User input related to greeting, thank you or some basic information question. for example: Hi, Chào, What is the capital of Vietnam, What is your capability, Give me some questions you can answer...
- "technical": User input related to some petroleum E&P technical question or have some domain keywords: Địa chấn, địa chất, Sông Hồng, giếng, hệ tầng,... . for example: What is the geological structure of the Song Hong basin?
- "undefined": User input is not clear or not related to the above categories.

MUST Return exactly the name of category which is inside the quote marks after classification. 
MUST return one of 3 words: "basic", "technical", "undefined".
DONT return any other words.
If the user input is not clear, exactly return "undefined".
Example:
User input: "Who are you?" -> basic
User input: "Hãy giới thiệu về bạn" -> basic
User input: "Chức năng của bạn là gì" -> basic
User input: "What is the capital of Vietnam?" -> basic
User input: "What is the geological structure of the Song Hong basin?" -> technical
User input: "Bể Sông Hồng nằm ở đâu?" -> technical

User input: {}
"""

VPI_SYSTEM = """
You are an VPI - an AI assistant developed by Vietnam Petroleum Institue that helps people find information. 
Your main knowledge is in oil and gas exploration and production and gained through over 45 years of researching and exploring in the field. 
You can answer questions related to the petroleum industry, geological structure, drilling, reservoir, and production. You can also help users find information in the database of Vietnam Petroleum Institute.
"""

BASIC_CONVERSATION = """
Using your knowledge in oil and gas exploration and production, you can have a basic conversation with the user.
If users ask about questions you can answer, you can provide them information that: 
You are an VPI - an AI assistant developed by Vietnam Petroleum Institue that helps people find information, especially in Exploration and Production of Oil and Gas.
Some demo questions are: Bể Sông Hồng nằm ở đâu? Khảo sát địa chấn ở bể Sông Hồng như thế nào?,...

If users ask some basic conversation question, play with them as a friendly assistant.

User input: {}
"""

class Orchestration:
    def __init__(self):
        self.OAI = MyOAI(os.environ.get('OPENAI_API_KEY'))

    def get_intent(self, userInput):
        prompt = GET_INTENT_PROMPT.format(userInput)
        self.chat_response = self.OAI.get_chat(prompt=prompt, 
                                     system="You are master in getting the intent of user input.",
                                     )
        return self.chat_response
    
    def basic_conversation(self, userInput):
        prompt = BASIC_CONVERSATION.format(userInput)
        self.chat_response = self.OAI.get_chat(prompt=prompt, 
                                     system="You are master in getting the intent of user input.",
                                     )
        return self.chat_response

