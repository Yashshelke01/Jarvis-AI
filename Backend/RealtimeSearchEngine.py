from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Load or create chat log
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)
    messages = []

def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    return Answer

def AnswerModifier(answer):
    lines = answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

SystemChatBot = [
    {"role": "system", "content": System},
]

def Information():
    current_date_time = datetime.datetime.now()

    return f"""
Use this real-time information if needed:
Day: {current_date_time.strftime("%A")}
Date: {current_date_time.strftime("%d")}
Month: {current_date_time.strftime("%B")}
Year: {current_date_time.strftime("%Y")}
Time: {current_date_time.strftime("%H")} hours, 
{current_date_time.strftime("%M")} minutes, 
{current_date_time.strftime("%S")} seconds.
"""

def RealtimeSearchEngine(prompt):
    global messages

    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)

    messages.append({"role": "user", "content": prompt})

    # Add Google search results
    search_data = GoogleSearch(prompt)

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [
            {"role": "system", "content": search_data},
            {"role": "system", "content": Information()},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=False
    )

    response = completion.choices[0].message.content

    messages.append({"role": "assistant", "content": response})

    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    return AnswerModifier(response)