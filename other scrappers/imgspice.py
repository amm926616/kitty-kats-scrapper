#!/usr/bin/env python

import os
import requests
from bs4 import BeautifulSoup
import time
import pyfiglet
from termcolor import colored
import math
import tkinter as tk
from tkinter import messagebox
import pyperclip

# Create ASCII art
ascii_art = pyfiglet.figlet_format("IMGSPICE", font="slant")
colored_ascii_art = colored(ascii_art, color="cyan")
print(colored_ascii_art)

print("\033[31mAuto Getting link from the clipboard\033[0m")
# Main URL of the page to scrape
url = pyperclip.paste()
print("URL: ", url)

# File to store downloaded URLs
downloaded_url_file = '/run/media/adam178/6abf3584-a2fd-495a-bdc1-b9f4dfee84e3/.metart/downloaded_url.txt'

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

# Send request to the main page
try:
    print("Sending request to the main page...")
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    print("Request successful!")
except requests.exceptions.RequestException as e:
    print(f"Error during request: {e}")
    exit()

# Directory to save the downloaded images
# Extract folder name from the last segment of the URL
folder_name = url.rstrip('/').split('/')[-1]
save_folder = os.path.join("/run/media/adam178/Storage/.MetArt-Second/", folder_name)

if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Parse the main page's HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Find all <a> tags with the class 'link--external'
print("Extracting redirect links...")
redirect_links = soup.find_all('a', class_='link--external')

# List to store the final image URLs
image_urls = []

# Loop through each redirect link, follow it, and extract the image URL
for link in redirect_links:
    href = link.get('href')
    if href:
        try:
            print(f"Following redirect URL: {href}")
            redirect_response = requests.get(href, headers=headers, timeout=10)
            redirect_response.raise_for_status()

            # Parse the redirected page's HTML
            redirect_soup = BeautifulSoup(redirect_response.text, 'html.parser')

            # Find the <img> tag with id 'imgpreview'
            img_tag = redirect_soup.find('img', id='imgpreview')
            if img_tag:
                img_url = img_tag.get('src')
                image_urls.append(img_url)
                print(f"Found image URL: {img_url}")
            else:
                print("Image tag with id 'imgpreview' not found.")

        except requests.exceptions.RequestException as e:
            print(f"Error during redirect request: {e}")

# Display all the collected image URLs
print("\nAll extracted image URLs:")
for img_url in image_urls:
    print(img_url)


# Download each image
for img_url in image_urls:
    try:
        img_name = os.path.basename(img_url)
        img_path = os.path.join(save_folder, img_name)

        # Skip downloading if the image already exists
        if os.path.exists(img_path):
            print(f"Image already exists, skipping: {img_name}")
            continue

        print(f"Downloading image: {img_name}")
        img_response = requests.get(img_url, headers=headers, timeout=10)
        img_response.raise_for_status()

        with open(img_path, 'wb') as img_file:
            img_file.write(img_response.content)

        print(f"Image saved: {img_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error during image download: {e}")

# Final message
print(f"\nAll images have been downloaded and saved to: {save_folder}")

def show_popup():
    # Create a new Tkinter window
    root = tk.Tk()
    # Hide the root window
    root.withdraw()
    # Show a pop-up message box
    messagebox.showinfo("Downloading Done", folder_name)
    # Destroy the root window after the pop-up is closed
    root.destroy()

# Call the function to show the pop-up
show_popup()