# Web Scraper and Algolia Indexer

This project scrapes product data from a specified URL(Rimowa) and indexes it in Algolia. It uses Python, Scrapy, Pyppeteer, and Docker.

## Prerequisites

- Docker

## Setup

1. **Clone the repository:**

   ```sh
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

2. **Create a `.env` file:**

   Create a `.env` file in the root directory of the project with the following content:

   ```env
   RUB_URL=https://api.exchangerate-api.com/v4/latest/USD
   SCRAPER_URL=https://www.rimowa.com/us/en/collection
   ALGOLIA_APP_ID=your_algolia_app_id
   ALGOLIA_API_KEY=your_algolia_api_key
   ALGOLIA_INDEX_NAME=your_algolia_index_name
   ```

   Replace the placeholder values with your actual environment variables.

3. **Build and run the Docker container:**

   ```sh
   docker build -t web_scraper_algolia .
   docker run  web_scraper_algolia
   ```

   This will build the Docker image and run the container using the environment variables specified in the `.env` file.

## Project Structure

- `main.py`: The main script that performs the scraping and indexing.
- `Dockerfile`: The Dockerfile to create a Docker image for the project.
- `requirements.txt`: The Python dependencies required for the project.
- `.env`: The environment variables for the project (not included in the repo, should be created as described).

## Dependencies

- Python 3.8
- aiohttp
- pyppeteer
- python-dotenv
- scrapy
- algoliasearch

## Running Locally (Without Docker)

1. **Install the dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

2. **Set up the environment variables:**

   Create a `.env` file as described above.

3. **Run the script:**

   ```sh
   python main.py
   ```

## License

This project is licensed under the MIT License.
