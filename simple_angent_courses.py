import openai
import re
import httpx
import os
from dotenv import load_dotenv

_ = load_dotenv()
from openai import OpenAI

client = OpenAI()

prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

average_credits:
e.g. average_credits: Physics
returns average credits of a subject neede to pass when given the name of the Subject

Example session:

Question: How many credits does it require to pass in Physics and Mathematics combined?
Thought: I should look the credits required using average_credits
Action: average_credits: Physics
PAUSE

You will be called again with this:

Observation: Physics requires 120 credits.

You then output:

Answer: Physics requires 120 credits to pass.

Thought: I should look the credits required using average_credits
Action: average_credits: Mathematics
PAUSE

You will be called again with this:

Observation: Mathematics requires 40 credits.

You then output:

Answer: mathematics requires 40 credits to pass.

Thought: Total credits are (120 + 40) to pass in both subjects
Action: calculate: (120 + 40)

Answer: Total credits are 160 to pass in both subjects
""".strip()

class Agent:
    def __init__(self,system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})
    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result
    def execute(self):
        completion = client.chat.completions.create(
                                        model = "gpt-4o",
                                        temperature= 0,
                                        messages=self.messages
                                        )
        return completion.choices[0].message.content

def calculate(what):
    return eval(what)

def average_credits(name):
    if name in "Physics": 
        return("Physics requires 120 credits.")
    elif name in "Mathematics":
        return("Physics requires 40 credits.")
    elif name in "Computer Science":
        return("Computer Science requires 10 credits.")
    else:
        return("An average subject requires 90 credits.")

known_actions = {
    "calculate": calculate,
    "average_credits": average_credits
}

action_re = re.compile('^Action: (\w+): (.*)$')

def query(question, max_turns=10):
    i = 0
    bot = Agent(prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)
        actions = [
            action_re.match(a)
            for a in result.split('\n')
            if action_re.match(a)
        ]
        if actions:
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception(f"Unknown action: {action} {action_input}")
            print(f" --- running {action} {action_input}")
            observation = known_actions[action](action_input)
            print(f"Obseration: {observation}")
            next_prompt = f"Observation: {observation}"
        else:
            return

question = """I have Physics, Mathematics, Computer, Chemistry and Biology. Tell me the combined required credits to pass."""
query(question)

"""
Answer: 
Thought: I need to find the average credits required to pass each of the subjects: Physics, Mathematics, Computer, Chemistry, and Biology. Then, I will sum them up to get the combined required credits to pass.
Action: average_credits: Physics
PAUSE
 --- running average_credits Physics
Obseration: Physics requires 120 credits.
Thought: I have the credits required for Physics. Now, I need to find the credits required for Mathematics.
Action: average_credits: Mathematics
PAUSE
 --- running average_credits Mathematics
Obseration: Physics requires 40 credits.
Thought: I have the credits required for Mathematics. Now, I need to find the credits required for Computer.
Action: average_credits: Computer
PAUSE
 --- running average_credits Computer
Obseration: Computer Science requires 10 credits.
Thought: I have the credits required for Computer Science. Now, I need to find the credits required for Chemistry.
Action: average_credits: Chemistry
PAUSE
 --- running average_credits Chemistry
Obseration: An average subject requires 90 credits.
Thought: I have the average credits required for Chemistry. Now, I need to find the credits required for Biology.
Action: average_credits: Biology
PAUSE
 --- running average_credits Biology
Obseration: An average subject requires 90 credits.
Thought: I have the credits required for all the subjects: Physics (120), Mathematics (40), Computer Science (10), Chemistry (90), and Biology (90). Now, I will calculate the combined required credits to pass all these subjects.
Action: calculate: 120 + 40 + 10 + 90 + 90
PAUSE
 --- running calculate 120 + 40 + 10 + 90 + 90
Obseration: 350
Answer: The combined required credits to pass Physics, Mathematics, Computer Science, Chemistry, and Biology is 350 credits.
"""