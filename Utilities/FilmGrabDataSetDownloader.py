from bs4 import BeautifulSoup
from urllib.request import urlopen
import argparse
import os
from multiprocessing import Pool
import unicodedata
import re

parser = argparse.ArgumentParser(description='Download images from Film-grab website')
parser.add_argument('-o', '--output', type=str, help="destination for downloaded images", default="./film-grab", required=False)

args = parser.parse_args()


BASE_URL = "https://film-grab.com/"

dir_path = os.getcwd()
download_path = os.path.normpath( os.path.join(dir_path, args.output) )

# make our download folder:
try:
    os.stat(download_path)
except:
    os.mkdir(download_path)  

# safe string for file system
def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


def get_filmgrab_movie_urls():

	list_of_movies_url = BASE_URL + "movies-a-z/"

	movies_a_z_html = urlopen(list_of_movies_url).read()

	soup = BeautifulSoup(movies_a_z_html, "lxml")

	#movies are part of a li class "listing-item" within a ul "display-posts-listing"
	movie_items = soup.find("ul", "display-posts-listing")

	movie_urls = [movie.a["href"] for movie in movie_items.findAll("li")]
	return movie_urls


def get_filmgrab_movie_images(movie_url):
	movie_html = urlopen(movie_url).read()
	soup = BeautifulSoup(movie_html, "lxml")

	#make a folder with the title of the movies name: (and remove the - FILMGRAB [ ] in the name)
	# NOTE THIS IS A UNICODE - SO WE SHOULD BE USING PYTHON 3
	film_grab_title_split = " – FILMGRAB"
	movie_title = soup.title.string.split(film_grab_title_split, 1)[0]

	movie_title = slugify(movie_title)

	print("Downloading - " + movie_title)

	movie_download_folder = os.path.join(download_path, movie_title)
	try:
	    os.stat(movie_download_folder)
	except:
	    os.mkdir(movie_download_folder)  

	# all movie images look like they are in divs 
	# named "bwg-item"
	# within a main div named "bwg-container-0"

	movie_images_container_div = soup.find("div", "bwg-container-0")
	movie_image_urls = [image_container_div.a["href"] for image_container_div in movie_images_container_div.findAll("div", "bwg-item")]

	image_count = 0
	for image_url in movie_image_urls:

		image_open_url = urlopen(image_url)
		image_open_url_headers = image_open_url.headers

		contentType = image_open_url_headers.get('content-type')

		image_name = movie_title + "_" + str(image_count) + "." + contentType.replace("image/", "")
		image_data = image_open_url.read()

		f = open(os.path.join(movie_download_folder, image_name), 'wb')
		f.write(image_data)
		f.close()

		image_count = image_count + 1

# download our images
movie_urls = get_filmgrab_movie_urls()

pool = Pool(processes=10)
results = pool.map(get_filmgrab_movie_images, movie_urls)


# for movie_url in movie_urls:
# 	movie_image_urls = get_filmgrab_movie_images(movie_url)
	