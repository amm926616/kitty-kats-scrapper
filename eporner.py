#!/usr/bin/env python

import os, subprocess
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pyfiglet
from termcolor import colored
import pyperclip
import time, wget

# Create ASCII art
ascii_art = pyfiglet.figlet_format("eporners", font="slant")

# Add color to the ASCII art
colored_ascii_art = colored(ascii_art, color="cyan")

# Print the colored ASCII art
print(colored_ascii_art)


def sanitize_folder_name(name):
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()

def extract_image_urls(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": url,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "DNT": "1"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve page content: {e}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract the title of the page to create a folder
    folder_name = os.path.join("/home/adam178/.eporners", sanitize_folder_name(url))
    
    os.makedirs(folder_name, exist_ok=True)
    
    # Find all div elements with class 'sg_gallery_meta'
    meta_divs = soup.find_all('div', class_='sg_gallery_meta')
    
    img_urls = []
    
    # Iterate over each meta div to find the corresponding img tag
    for meta_div in meta_divs:
        img_tag = meta_div.find_previous('img')  # Find the img tag before the div
        if img_tag and img_tag.has_attr('src'):
            img_url = img_tag['src']
            
            # Remove the dimension string from the URL
            if '_296x1000' in img_url:
                img_url = img_url.replace('_296x1000', '')
            
            img_urls.append(img_url)
    
    return img_urls, folder_name

def download_images(img_urls, folder_name, max_retries=3):
    downloaded_images = set(os.listdir(folder_name))
    
    for img_url in img_urls:
        img_name = os.path.basename(img_url)
        img_path = os.path.join(folder_name, img_name)
        
        if img_name in downloaded_images:
            print(f"'{img_name}' already downloaded. Skipping.")
            continue
        
        for attempt in range(max_retries):
            try:
                print(f"Downloading {img_url}...")
                wget.download(img_url, out=img_path)
                print(f"\nDownloaded '{img_name}' successfully.")
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    print(f"Failed to download '{img_name}' after {max_retries} attempts.")
                    continue
                time.sleep(2)  # Wait before retrying


def download_files(urls_file, download_folder):
    # Ensure the download folder exists
    os.makedirs(download_folder, exist_ok=True)

    # Define the wget command
    wget_command = [
        'wget',
        '-i', urls_file,                  # Input file with URLs
        '--directory-prefix=' + download_folder,  # Directory to save files
        '--no-clobber',                   # Skip downloading files that already exist
        '--quiet'                         # Run wget quietly (optional)
    ]

    try:
        # Run the wget command
        result = subprocess.run(wget_command, check=True, text=True, capture_output=True)
        print("Download completed successfully.")
        print(result.stdout)  # Print the output of the wget command

    except subprocess.CalledProcessError as e:
        print(f"Download failed with error code {e.returncode}")
        print(e.stderr)  # Print any error messages from wget


def download_files(download_folder):
    # Ensure the download folder exists
    os.makedirs(download_folder, exist_ok=True)
    print(f"created container folder {download_folder} in .eporners")

    # Define the wget command
    wget_command = [
        'wget',
        '-i', "urls.txt",                  # Input file with URLs
        '--directory-prefix=' + download_folder,  # Directory to save files
        '--no-clobber',                   # Skip downloading files that already exist
        '--quiet'                         # Run wget quietly (optional)
    ]

    try:
        # Run the wget command
        print("Start downloading. Please wait for a while....")
        result = subprocess.run(wget_command, check=True, text=True, capture_output=True)
        print("Download completed successfully.")
        print(result.stdout)  # Print the output of the wget command

    except subprocess.CalledProcessError as e:
        print(f"Download failed with error code {e.returncode}")
        print(e.stderr)  # Print any error messages from wget

url = input("URL: ")
img_urls, download_folder = extract_image_urls(url)

# Open the file in write mode
with open('urls.txt', 'w') as file:
    # Write each item to the file
    for item in img_urls:
        file.write(item + '\n') 

print("Image Urls are extracted and saved to urls.txt file in home directory")

download_files(download_folder)

