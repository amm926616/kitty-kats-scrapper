#!/usr/bin/env python

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pyfiglet
from termcolor import colored
import pyperclip

# Create ASCII art
ascii_art = pyfiglet.figlet_format("pornhats", font="slant")

# Add color to the ASCII art
colored_ascii_art = colored(ascii_art, color="cyan")

# Print the colored ASCII art
print(colored_ascii_art)

def download_images(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve page content: {e}")
        return
    
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract the title of the page to create a folder
    title = soup.title.string.strip()
    folder_name = os.path.join("/home/adam178/.pornhats", title)
    
    # Create a folder if it doesn't exist
    os.makedirs(folder_name, exist_ok=True)
    
    # Find all elements with class 'thumb-bl grid-item'
    thumb_items = soup.find_all('div', class_='thumb-bl grid-item')
    
    # Track downloaded images
    downloaded_images = set(os.listdir(folder_name))
    
    # Download each image
    for thumb_item in thumb_items:
        img_url = thumb_item['href']  # Get the href attribute
        
        if img_url.endswith(('.jpg', '.jpeg', '.png')):
            img_name = os.path.basename(img_url)
            
            if img_name in downloaded_images:
                print(f"Skipping {img_name}, already downloaded.")
                continue
            
            try:
                img_response = requests.get(img_url)
                img_response.raise_for_status()
                
                with open(os.path.join(folder_name, img_name), 'wb') as img_file:
                    img_file.write(img_response.content)
                print(f"Downloaded: {img_name}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download image {img_name}: {e}")

print("\033[31mAuto Getting link from the clipboard\033[0m")
# Main URL of the page to scrape
url = pyperclip.paste()
print("URL: ", url)

# Call the function to download images
download_images(url)
