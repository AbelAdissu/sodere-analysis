import os
import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
import time

class SoderestoreSpider(scrapy.Spider):
    name = 'soderestore'
    allowed_domains = ['soderestore.com']
    start_urls = ['https://soderestore.com/Books-%E1%88%98%E1%8D%83%E1%88%85%E1%8D%8D%E1%89%B5-c35241255']

    def __init__(self, *args, **kwargs):
        super(SoderestoreSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()  # Initialize Selenium WebDriver
        self.driver.set_page_load_timeout(60)  # Set timeout for loading pages
        self.all_books_data = []  # List to store all book data
        self.total_books = 0  # Counter for total books

        # Create the images directory if it doesn't exist
        if not os.path.exists('images'):
            os.makedirs('images')

    def parse(self, response):
        try:
            self.driver.get(response.url)  # Load the initial URL with Selenium

            while True:
                self.log(f'Processing page: {self.driver.current_url}')
                self.scrape_current_page()  # Scrape the data from the current page
                self.log(f'Total books collected so far: {self.total_books}')

                try:
                    # Wait for and click the "next" button to load the next page
                    next_button = WebDriverWait(self.driver, 20).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.ec-link.ec-link--muted.link--icon-append.pager__button.pager__button--next'))
                    )
                    if next_button and 'disabled' not in next_button.get_attribute('class'):
                        self.driver.execute_script("arguments[0].click();", next_button)
                        # Wait until the next page's products are loaded
                        WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.grid-product'))
                        )
                        time.sleep(5)  # Ensure the next page is fully loaded
                    else:
                        self.log('No more pages found or next button is disabled.')
                        break  # Exit the loop if no more pages are found or the next button is disabled
                except Exception as e:
                    self.log(f'Error during pagination: {e}')
                    break  # Exit the loop if an error occurs

            self.log(f'Total books collected: {self.total_books}')

            # Save all collected data to a JSON file
            with open('books_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.all_books_data, f, ensure_ascii=False, indent=4)

        except Exception as e:
            self.log(f'An error occurred: {e}')
        finally:
            self.driver.quit()  # Ensure the WebDriver is properly closed

    def scrape_current_page(self):
        sel = Selector(text=self.driver.page_source)  # Create a Scrapy Selector from the page source
        books = sel.css('div.grid-product')  # Select all books on the page
        self.log(f'Found {len(books)} books on the current page.')

        for i, book in enumerate(books):
            try:
                # Extract data for each book
                link = book.css('a.grid-product__image::attr(href)').get()
                full_link = self.driver.current_url + link if link else None
                title = book.css('a.grid-product__title > div.grid-product__title-inner::text').get()
                image_url = book.css('img.grid-product__picture::attr(src)').get()
                shadow_text = book.css('div.grid-product__shadow-inner::text').get()
                price = book.css('div.grid-product__price > div > div::text').get()
                additional_title = book.css('div.grid-product__title-inner::text').get()

                # Save the image and update image path
                image_path = None
                if image_url:
                    image_path = self.download_image(image_url, self.total_books)

                # Store the collected data in a dictionary
                book_data = {
                    'full_link': full_link,
                    'title': title,
                    'image_path': image_path,
                    'shadow_text': shadow_text,
                    'price': price,
                    'additional_title': additional_title,
                }
                self.all_books_data.append(book_data)  # Add the book data to the list
                self.total_books += 1  # Increment the total books counter
            except Exception as e:
                self.log(f'Error scraping book: {e}')

    def download_image(self, url, index):
        for attempt in range(3):  # Retry logic for downloading images
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    image_path = f'images/book_cover_{index}.jpg'  # Define the image file path
                    with open(image_path, 'wb') as f:
                        f.write(response.content)  # Save the image content to a file
                    self.log(f'Downloaded image {index}: {url}')
                    return image_path  # Return the local image path
            except Exception as e:
                self.log(f'Attempt {attempt + 1} failed to download image {index} from {url}: {e}')
                time.sleep(2)  # Wait before retrying
        self.log(f'Failed to download image {index} from {url} after 3 attempts')
        return None  # Return None if the download failed

    def closed(self, reason):
        self.driver.quit()  # Ensure the WebDriver is properly closed
