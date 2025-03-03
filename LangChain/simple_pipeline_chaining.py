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
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from copy import deepcopy

instruct_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)
prompt1 = ChatPromptTemplate.from_messages([("user", (
    "INSTRUCTION: Only respond in rhymes"
    "\n\nPROMPT: {input}"
))])

prompt2 =  ChatPromptTemplate.from_messages([("user", (
    "INSTRUCTION: Only responding in rhyme, change the topic of the input poem to be about {topic}!"
    " Make it happy! Try to keep the same sentence structure, but make sure it's easy to recite!"
    " Try not to rhyme a word with itself."
    "\n\nOriginal Poem: {input}"
    "\n\nNew Topic: {topic}"
))])

## These are the main chains, constructed here as modules of functionality.
chain1 = prompt1 | instruct_llm | StrOutputParser()  ## only expects input
chain2 = prompt2 | instruct_llm | StrOutputParser()  ## expects both input and topic


def rhyme_chat2_stream(message, history, return_buffer=True):
    '''This is a generator function, where each call will yield the next entry'''

    first_poem = None
    for entry in history:
        if entry[0] and entry[1]:
            ## If a generation occurred as a direct result of a user input,
            ##  keep that response (the first poem generated) and break out
            first_poem = "\n\n".join(entry[1].split("\n\n")[1:-1])
            break

    if first_poem is None:
        ## First Case: There is no initial poem generated. Better make one up!

        buffer = "Oh! I can make a wonderful poem about that! Let me think!\n\n"
        yield buffer

        ## Iterate over stream generator for first generation
        inst_out = ""
        chat_gen = chain1.stream({"input" : message})
        for token in chat_gen:
            inst_out += token
            buffer += token
            yield buffer if return_buffer else token

        passage = "\n\nNow let me rewrite it with a different focus! What should the new focus be?"
        buffer += passage
        yield buffer if return_buffer else passage

    else:
        buffer = f"Sure! Here you go!\n\n"
        yield buffer
        
        ## iterate over stream generator for second generation
        chat_gen = chain2.stream({"input" : first_poem, "topic" : message})
        for token in chat_gen:
            buffer += token
            yield buffer if return_buffer else token
        passage = "\n\nThis is fun! Give me another topic!"
        buffer += passage
        yield buffer if return_buffer else passage


## Simple way to initialize history for the ChatInterface
chatbot = gr.Chatbot(value = [[None, "Let me help you make a poem! What would you like for me to write?"]])

## IF USING COLAB: Share=False is faster
gr.ChatInterface(rhyme_chat2_stream, chatbot=chatbot).queue().launch(debug=True, share=True)