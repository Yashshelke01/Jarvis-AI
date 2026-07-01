from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

#Load Environment variables from .env file
env_vars = dotenv_values(".env")

#retrieve specific environment variables for username,assistant name and API Key
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

#Initialise the Groq client using the provided api key
client = Groq(api_key=GroqAPIKey)

#Initialize an empty list to store chat messages
messages = []

#Define a system message that provides context to the AI chatbot about its role and behaviour
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# A list of system instructions to chatbot
SystemChatBot = [
    {"role": "system","content": System}
]

# Attempt to load the chat log from JSON file
try:
    with open(r"Data\ChatLog.json","r") as f:
        messages = load(f)
except FileNotFoundError:
    #If the file doesn't exists, JSON file to store chat logs
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

#Function to get real-time date and time information
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    # Format the information into string
    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time : {hour} hours :{minute} minutes : {second} seconds.\n"
    return data

#Function to modify the chatbots response for better formatting
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

#Main chatbot function to handle user queries
def ChatBot(Query):
    """This function sends the user's query to the chatbot and returns the AI's response."""

    try:
        #Load the existing chat log from JSON file
        with open(r"Data\ChatLog.json","r") as f:
            messages = load(f)

        #append the user's query to message list
        messages.append({"role":"user","content":f"{Query}"})

        #make a request to the Groq API for a response.
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role":"system","content":RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""  #Initialize an empty string to store AI's response

        #Process the streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")

        #Append the chatbots response to the messages list 
        messages.append({"role": "assistant", "content": Answer})

        #Save the updated chat log to JSON file 
        with open(r"Data\ChatLog.json","w") as f:
            dump(messages, f, indent=4)

        #return the formatted response 
        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"Error: {e}")

        # Reset chat log safely
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)

        return "Sorry, I encountered an error. Please try again."
    
#Main program entry point
if __name__ == "__main__":
    while True:
        user_input = input("Enter your Question: ") #prompt the user for a question 
        print(ChatBot(user_input))   # call the chatbot function and print its response
   

