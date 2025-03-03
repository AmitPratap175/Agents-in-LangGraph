import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set variables into system environment
for key, value in os.environ.items():
    os.environ[key] = value  # Ensures the variable is available globally

import gradio as gr
def rhyme_chat_stream(message, history):
    ## This is a generator function, where each call will yield the next entry
    buffer = ""
    for token in rhyme_chain.stream({"input" : message}):
        buffer += token
        yield buffer

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system","Only respond in rhymes"),
        ("human", "{input}"),
    ]
)

rhyme_chain = prompt | llm | StrOutputParser()
# result = rhyme_chain.invoke(
#     {
#         "input": "I love programming.",
#     }
# )
# # ai_msg = llm.invoke(messages)
# print(result)

## Uncomment when you're ready to try this.
demo = gr.ChatInterface(rhyme_chat_stream).queue()
window_kwargs = {} # or {"server_name": "0.0.0.0", "root_path": "/7860/"}
demo.launch(share=True, debug=True, **window_kwargs) 

## IMPORTANT!! When you're done, please click the Square button (twice to be safe) to stop the session.