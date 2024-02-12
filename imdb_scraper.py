import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

def _get_soup(page):
    '''
    Get the BeautifulSoup object from a url.
    Args:
        - page(str) = page to scrape
            Options: 'most_popular_movies', 'top_250_movies', 'top_english_movies', 'top_250_tv'
    Returns:
        - soup(BeautifulSoup) = BeautifulSoup object
    '''
    # Define user agent and headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    # Send a get request and parse using BeautifulSoup with headers
    if page == 'most_popular_movies':
        url = 'https://www.imdb.com/chart/moviemeter/'
    
    elif page == 'top_250_movies':
        url = 'https://www.imdb.com/chart/top/'
    
    elif page == 'top_english_movies':
        url = 'https://www.imdb.com/chart/top-english-movies/'

    # Make the request with headers
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else:
        print(f"Error: Failed to fetch the page. Status code: {response.status_code}")
        return None



def _scrape_movies(soup):
    # Find all movie names in the url
    movie_names = []
    movie_years = []
    movie_ratings = []
    vote_counts = []
    movie_duration = []
    movie_rated = []

    # Count missing data
    missing_data_count = {'title': 0, 'release_year': 0, 'duration': 0, 'rated':0, 'rating': 0, 'vote_count': 0}
    
    # Count rows inserted and missing values replaced
    rows_inserted = 0
    missing_values_replaced = 0

    # Find all movie in the url
    listRefs = soup.find_all('li', class_='ipc-metadata-list-summary-item')

    # Collect movie title, release year, ratings, and user votings
    for movie in listRefs:
        try:
            movie_names.append(movie.find('h3', class_='ipc-title__text').text)
        except:
            movie_names.append(-1)
            missing_data_count['title'] += 1

        try:
            yeardiv = movie.find('div', class_='cli-title-metadata')
            year_span = yeardiv.find('span', class_='cli-title-metadata-item')
            year = year_span.text
            movie_years.append(int(year))
        except:
            movie_years.append(-1)
            missing_data_count['release_year'] += 1

        try:
            duration_span = yeardiv.find_all('span', class_='cli-title-metadata-item')[1]
            duration_str = duration_span.text

            # Extracting hours and minutes
            hours, minutes = map(int, duration_str.replace('h', '').replace('m', '').split())

            # Converting to total minutes
            total_minutes = hours * 60 + minutes
            movie_duration.append(total_minutes)
        except:
            movie_duration.append(-1)
            missing_data_count['duration'] += 1

        try:
            rated_spans = yeardiv.find_all('span', class_='cli-title-metadata-item')
            rated_span = rated_spans[2] if len(rated_spans) > 2 else None
            rated_value = rated_span.text
            movie_rated.append(rated_value)
        except:
            movie_rated.append(-1)
            missing_data_count['rated'] += 1

        try:
            rating_span = movie.find('span', class_='ipc-rating-star--voteCount')
            movie_ratings.append(float(rating_span.previous_sibling.strip()))    
        except:
            movie_ratings.append(-1)
            missing_data_count['rating'] += 1

        try:
            votes_str = rating_span.get_text(strip=True)

            # Removing parentheses and handling suffixes
            numeric_value_str = votes_str[1:-1]
            multiplier = 1  # Default multiplier

            if numeric_value_str.endswith('M'):
                numeric_value_str = numeric_value_str.rstrip('M')
                multiplier = 1e6  # 1 million
            elif numeric_value_str.endswith('K'):
                numeric_value_str = numeric_value_str.rstrip('K')
                multiplier = 1e3  # 1 thousand

            # Converting to float with the appropriate multiplier
            numeric_value = float(numeric_value_str) * multiplier

            vote_counts.append(numeric_value)

        except:
            vote_counts.append(-1)
            missing_data_count['vote_count'] += 1

    # Create a dataframe
    movie_df = pd.DataFrame({'movie_name': movie_names, 'movie_year': movie_years, 'duration_min':movie_duration, 'rated':movie_rated, 'movie_rating': movie_ratings, 'vote_count': vote_counts})

    # Add movie_id
    movie_df['movie_id'] = movie_df.index + 1

    # reorder columns
    movie_df = movie_df[['movie_id', 'movie_name', 'movie_year', 'duration_min', 'rated', 'movie_rating', 'vote_count']]

    # Count rows inserted
    rows_inserted = len(movie_df)

    # Count missing values replaced by -1
    missing_values_replaced = sum(movie_df.isna().sum())

    return movie_df
