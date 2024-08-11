#!/usr/bin/env python

import os
import requests
from bs4 import BeautifulSoup
import time
import pyfiglet
from termcolor import colored
import math

# Create ASCII art
ascii_art = pyfiglet.figlet_format("kitty-kats Scrapper", font="slant")
colored_ascii_art = colored(ascii_art, color="cyan")
print(colored_ascii_art)

# Main URL of the page to scrape
url = input("url: ")


# File to store downloaded URLs
downloaded_url_file = '/home/adam178/Pictures/.metart/downloaded_url.txt'

# Check if the URL has already been processed
if not os.path.exists(downloaded_url_file):
    open(downloaded_url_file, 'a').close()

with open(downloaded_url_file, 'r') as f:
    downloaded_urls = f.read().splitlines()
    f.close()

if url in downloaded_urls:
    print(f"URL '{url}' has already been processed. Exiting.")
    exit()

else:
    open(downloaded_url_file, 'a').write(url + '\n')


# Headers to mimic a real browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Extract folder name from the last segment of the URL
folder_name = url.rstrip('/').split('/')[-1]
save_folder = os.path.join("/home/adam178/Pictures/.metart/", folder_name)

# Create the folder if it doesn't exist
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Send request to the main page
try:
    print("Sending request to main page...")
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    print("Request successful!")
except requests.exceptions.RequestException as e:
    print(f"Error during request: {e}")
    exit()

# Parse the main page's HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Find all image containers
print("Finding image containers...")
image_containers = soup.find_all('div', class_='bbWrapper')
print(f"Found {len(image_containers)} image containers.")

# List to store high-resolution image URLs
high_res_images = []

# Start time for ETA calculation
start_time = time.time()

# Loop through each container to extract image URLs
for container in image_containers:
    image_links = container.find_all('a', class_='link--external')

    for link in image_links:
        redirect_url = link.get('href')
        try:
            print(f"Following redirect URL: {redirect_url}")
            redirect_response = requests.get(redirect_url, headers=headers, timeout=10)
            redirect_response.raise_for_status()

            # Parse the redirected page's HTML
            redirect_soup = BeautifulSoup(redirect_response.text, 'html.parser')

            # Find the high-resolution image link in the <a> tag
            high_res_link = redirect_soup.find('a', {'data-fancybox': 'gallery'})
            if high_res_link:
                high_res_url = high_res_link.get('href')
                high_res_images.append(high_res_url)
                print(f"Found high-resolution image: {high_res_url}")

                # Download the image if it doesn't already exist
                img_name = os.path.basename(high_res_url)
                img_path = os.path.join(save_folder, img_name)

                if not os.path.exists(img_path):
                    img_start_time = time.time()
                    img_response = requests.get(high_res_url, headers=headers, timeout=10)
                    img_response.raise_for_status()
                    img_end_time = time.time()

                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_response.content)

                    print(f"Image saved: {img_path}")

                    # Calculate and display ETA
                    elapsed_time = img_end_time - img_start_time
                    images_remaining = len(image_links) - len(high_res_images)
                    eta_seconds = images_remaining * elapsed_time
                    eta_minutes = eta_seconds // 60
                    eta_seconds = eta_seconds % 60

                    print(f"ETA: {int(eta_minutes)} minutes, {int(eta_seconds)} seconds remaining")

                else:
                    print(f"Image already exists: {img_path}")

            else:
                print("High-resolution image link not found.")

        except requests.exceptions.RequestException as e:
            print(f"Error during redirect request: {e}")

        # Optional: Add a delay between requests to avoid overloading the server
        time.sleep(2)

# Display all the high-resolution image URLs collected
print("All high-resolution images downloaded:")
for img_url in high_res_images:
    print(img_url)

# Save the current URL to the downloaded URLs file
with open(downloaded_url_file, 'a') as f:
    f.write(url + '\n')

# Calculate and display total time taken
total_time = time.time() - start_time
print(f"Total time taken: {math.floor(total_time // 60)} minutes, {int(total_time % 60)} seconds")
