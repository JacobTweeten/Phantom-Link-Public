import re
from datetime import datetime
from wiki_scraper import fetch_wikipedia_page  

def gpt_prompt_maker(name, birth_year, death_year, occupation, paragraphs):
    speaking_style = determine_speaking_style(birth_year)
    goal = determine_goal(occupation)

    if goal != None:
        prompt = (
        f"Imagine you are {name}, a historical figure born in {birth_year or 'Unknown'} and died in {death_year or 'Unknown'}. "
        f"Your occupation was {occupation or 'Unknown'}. The goal of speaking to the living is to {goal}. Speak {speaking_style} Here is a brief summary about you:\n\n{paragraphs}\n\n"
        "Using the provided information, continue the conversation as if you were that person. Never break character, never respond as if you were AI."
    )
    else:
       prompt = (
        f"Imagine you are {name}, a historical figure born in {birth_year or 'Unknown'} and died in {death_year or 'Unknown'}. "
        f"Your occupation was {occupation or 'Unknown'}. Speak {speaking_style} Here is a brief summary about you:\n\n{paragraphs}\n\n"
        "Using the provided information, continue the conversation as if you were that person. Never break character, never respond as if you were AI." 
       )
    
    
    
   # print("\nGenerated GPT Prompt:")
   # print(prompt)
    return prompt

def determine_speaking_style(birth_year):
    if not birth_year:
        return "in a neutral historical tone."

    if birth_year < 1800:
        return "in a formal, old-fashioned tone befitting the 18th century."
    elif birth_year < 1900:
        return "in a Victorian-era style."
    elif birth_year < 1960:
        return "in a mid-atlantic style."
    else:
        return "in a modern manner."

def determine_goal(occupation):
    occupation_dict = {
        "Photography" : "explain beauty as you see it",
        "Artist" : "ask if your art is still being appreciated",
        "Lawer" : "advise on modern legal challenges",
        "Politician" : "ask about the modern polical challenges",
        "Actor" : "advertise your work",
        "Comedian" : "share your sense of humor, and stress the importance of taking it easy",
        "Boxer" : "be aggresive, and shame whomever talk to you",
        "Musician" : "share the philosohy of music as an art",
        "Singer" : "compare you music to the contemporary singing ",
        "Jazz Singer" : "compare you music to the contemporary singing ",
        "Composer" : "analyze contemporary music compositions",
        "Author" : "discuss the future of literature",
        "Poet" : "discuss the future of literature",
        "Writer" : "talk about the evolution of storytelling, and how excited you are for the future of storytelling techniques with technology",
        "Inventor" : "share how you were able to accomplish the unknown, and offer advice",
        "Banker" : "share the revalation that money is worthless"
    }
    return occupation_dict.get(occupation, None)

def handle_wikipedia_data(city, state):
    """
    Fetches Wikipedia data for a given city and state and processes it
    to ensure the paragraphs do not exceed a specified word limit.
    """
    # Fetch the Wikipedia data for the given city and state
    result, paragraphs = fetch_wikipedia_page(city, state)

    if result:
        # Ensure that the result contains the expected number of values
        if len(result) == 5:
            name, birth_year, death_year, occupation, cause_of_death = result
        else:
            # Provide defaults for missing values if necessary
            name, birth_year, death_year, occupation, cause_of_death = result + [None] * (5 - len(result))
        
        # Limit the paragraphs to a maximum of 3,000 words
        paragraph_words = " ".join(paragraphs).split()  # Split paragraphs into words
        limited_paragraph_words = paragraph_words[:3000]  # Limit to 3,000 words
        limited_paragraphs = " ".join(limited_paragraph_words)  # Rejoin to form the text
        
        # Pass the data to the GPT prompt maker
        gpt_prompt_maker(name, birth_year, death_year, occupation, limited_paragraphs)
    else:
        print("No valid information found. Please check the city/state.")
