import os
from imdb_scraper import _get_soup, _scrape_movies

def main():
    page_name = 'top_english_movies'
    soup = _get_soup(page=page_name)
    movies_df = _scrape_movies(soup)
    
    # Create a 'data' folder if it doesn't exist
    data_folder = 'data'
    os.makedirs(data_folder, exist_ok=True)
    
    csv_file_path = os.path.join(data_folder, f"{page_name}.csv")
    
    movies_df.to_csv(csv_file_path, index=False)

    # Print summary with CSV file name
    print(f"Summary: \nCSV File: {csv_file_path}\nRows Inserted: {len(movies_df)}")



if __name__ == '__main__':
    main()
