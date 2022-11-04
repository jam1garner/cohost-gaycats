import urllib
import praw
import time
import os
from urllib.parse import urlparse

subreddits = [
    #"IllegallySmolCats",
    #("catshuggingcats", 300),
    #("UpCloseCatPictures", 100)
]

global images_downloaded
images_downloaded = 0

def print_downloaded():
    global images_downloaded

    print(f"Downloaded {images_downloaded} images")

def extract_food(title: str) -> str:
    pass

def download_subreddit(reddit, subreddit, limit=1000, food=False):
    global images_downloaded

    top = reddit.subreddit(subreddit).top(limit=limit)
    top_posts = [post for post in top]
    non_vids = [post for post in top_posts if not "v.redd" in post.url]

    # reddit galleries
    gallery = [post for post in non_vids if 'reddit.com/gallery' in post.url]

    # i.redd.it urls
    ireddit = [post for post in non_vids if 'i.redd.it' in post.url]

    # filter out reddit images
    other = [post for post in non_vids if not (post in gallery or post in ireddit)]

    # imgur direct links
    imgur = [post for post in other if 'i.imgur.com' in post.url]

    # Download reddit galleries
    for post in gallery:
        image_dict = post.media_metadata
        for image_item in image_dict.values():
            try:
                largest_image = image_item['s']
                image_url = largest_image['u']

                if food:
                    if post.title.lower()
                    path = + os.path.splitext(urlparse(image_url.split('?')[0]).path)[1]
                else:
                    path = os.path.basename(urlparse(image_url.split('?')[0]).path)

                download_path = f'cats/{path}'
                if not os.path.exists(download_path):
                    urllib.request.urlretrieve(image_url, download_path)

                    images_downloaded += 1
            except Exception as e:
                print(e)
                print("Error, sleeping...")
                time.sleep(3)

    print_downloaded()

    # Download direct links
    for post in ireddit + imgur:
        try:
            image_url = post.url
            path = os.path.basename(urlparse(image_url.split('?')[0]).path)

            download_path = f'cats/{path}'
            if not os.path.exists(download_path):
                urllib.request.urlretrieve(image_url, download_path)

                images_downloaded += 1
        except Exception as e:
            print(e)
            print("Error, sleeping...")
            time.sleep(3)

    print_downloaded()

reddit = praw.Reddit("cat_scraper")

# Generic subreddits
for sub in subreddits:
    if type(sub) == tuple:
        name, limit = sub
        download_subreddit(reddit, name, limit=limit)
    elif type(sub) == str:
        download_subreddit(reddit, name)
    else:
        raise Exception(f"Invalid type {type(sub)}")

# Cats named food
download_subreddit(reddit, "CatsCalledFood", limit=500, food=True)
