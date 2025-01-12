import requests
from bs4 import BeautifulSoup
import random
import re

def fetch_wikipedia_page(city, state):
    if not city or not state:
        print("Error: City or state is None.")
        return None, []  # Return None if city or state is not provided

    city = city.replace(' ', '_')
    state = state.replace(' ', '_')
    url = f"https://en.wikipedia.org/wiki/List_of_people_from_{city},_{state}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return fetch_and_parse_wikipedia_page(url)

    except requests.exceptions.RequestException as e:
        # Perform a Google search if the Wikipedia page is not found
        query = f"Wikipedia page for People that Lived In {city}, {state}"
        google_search_url = f"https://www.google.com/search?q={query}"

        try:
            search_response = requests.get(google_search_url, headers={"User-Agent": "Mozilla/5.0"})
            search_response.raise_for_status()

            search_soup = BeautifulSoup(search_response.text, 'html.parser')
            search_results = search_soup.find_all('a', href=True)
            wikipedia_links = [link['href'] for link in search_results if 'wikipedia.org' in link['href']]

            if wikipedia_links:
                first_wikipedia_link = wikipedia_links[0]
                cleaned_link = first_wikipedia_link.split('&')[0].replace('/url?q=', '')
                if cleaned_link.startswith('/wiki/'):
                    cleaned_link = f"https://en.wikipedia.org{cleaned_link}"
                return fetch_and_parse_wikipedia_page(cleaned_link)

            else:
                print(f"No Wikipedia results found for {city}, {state}.")
                return None, []  # Handle case where no results were found

        except requests.exceptions.RequestException as e:
            print(f"Error performing the Google search: {e}")
            return None, []  # Return None if search fails


def fetch_and_parse_wikipedia_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').get_text()
        print(f"Page Title: {title}")

        notable_people = []

        for list_item in soup.find_all('a', href=True):
            href = list_item['href']
            if href.startswith('/wiki/') and ':' not in href and '#' not in href:
                full_url = f"https://en.wikipedia.org{href}"
                notable_people.append(full_url)

        while notable_people:
            random_person_url = random.choice(notable_people)

            try:
                person_response = requests.get(random_person_url)
                person_response.raise_for_status()
                person_soup = BeautifulSoup(person_response.text, 'html.parser')

                if is_person_deceased(person_soup):
                    person_title = person_soup.find('title').get_text()
                    print(f"\nFound deceased person's Wikipedia page: {person_title}")
                    print(f"URL: {random_person_url}")

                    paragraphs = []
                    for paragraph in person_soup.select('p'):
                        if paragraph.get_text(strip=True):
                            paragraphs.append(paragraph.get_text())

                    # Return both extracted details and the paragraphs
                    name, birth_year, death_year, occupation = extract_person_details(person_soup)
                    return (name, birth_year, death_year, occupation), paragraphs

                else:
                    notable_people.remove(random_person_url)

            except requests.exceptions.RequestException:
                notable_people.remove(random_person_url)

        if not notable_people:
            print("No valid deceased pages found.")
            return None, []  # Return None if no valid deceased people found

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the Wikipedia page: {e}")
        return None, []  # Return None in case of errors

def extract_person_details(person_soup):
    try:
        name = person_soup.find('h1', {'id': 'firstHeading'}).get_text()
        print(f"NAME: {name}")

        infobox = person_soup.find('table', {'class': 'infobox'})
        birth_year = None
        death_year = None
        occupation = None  # Initialize occupation

        if infobox:
            birth_row = infobox.find('th', text='Born')
            death_row = infobox.find('th', text='Died')
            occupation_row = infobox.find('th', text='Occupation')  # Occupation row

            if birth_row:
                birth_date = birth_row.find_next('td').get_text(strip=True)
                birth_year = extract_year_from_date(birth_date)
                print(f"BIRTH YEAR: {birth_year}")

            if death_row:
                death_info = death_row.find_next('td')
                if death_info:
                    death_year_match = re.search(r'(\d{4})', death_info.text)
                    if death_year_match:
                        death_year = death_year_match.group(1)
                        print(f"Death year: {death_year}")
                    else:
                        print("Death year not found in the death information.")

            # Extract occupation if available
            if occupation_row:
                print("Occupation row found!")
                occupation_info = occupation_row.find_next('td').get_text(strip=True)
                occupation = occupation_info
                print(f"Occupation: {occupation}")

        else:
            print("No infobox found.")

        return name, birth_year, death_year, occupation

    except Exception as e:
        print(f"Error extracting details: {e}")
        return None, None, None, None


def extract_year_from_date(date_string):
    match = re.search(r'\d{4}', date_string)
    return int(match.group(0)) if match else None

def send_to_gpt_prompt_maker(name, birth_year, death_year, occupation, paragraphs):
    paragraphs_string = "\n".join(paragraphs)
    from gpt_prompt_maker import gpt_prompt_maker
    gpt_prompt_maker(name, birth_year, death_year, occupation, paragraphs_string)

def is_person_deceased(person_soup):
    infobox = person_soup.find('table', {'class': 'infobox'})
    
    if infobox:
        born_row = infobox.find('th', text='Born')
        died_row = infobox.find('th', text='Died')
        
        if born_row and died_row:
            birth_date = born_row.find_next('td').get_text(strip=True)
            death_date = died_row.find_next('td').get_text(strip=True)
            
            if birth_date and death_date:
                return True

    return False
