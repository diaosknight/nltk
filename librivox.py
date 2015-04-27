from urllib import request
from bs4 import BeautifulSoup
import re
from nltk import word_tokenize
from nltk.corpus import words
import math
import time
import random

posts =[]
counter = 0
max_sleep = 2.0


def download(url):
    time.sleep(random.random() * max_sleep)
    html = request.urlopen(url).read().decode('utf8')
    return BeautifulSoup(html)


def scrape_posts(url):
	"""Scrapes Librivox posts and appends the content of each post to a list containing its posts"""
	page_posts = []
	#gets the url
	soup = download(url)
	
	#gets the text of the posts and appends them to the posts list.
	soup_posts = soup.find_all(class_="postbody")
	for post in soup_posts:
		post_text = post.get_text()
		# only pulls in those posts not prefaced with underscores (because those are going to be user signatures)
		if not re.findall(r'_+', post_text):
			page_posts.append(post_text) 		
	
	return page_posts


def paginator(url, counter, per_page):

	# need a regex to find the last number of the url, the pagination number.
	pattern = re.compile(r'[0-9]+$')

	# initializes the counter.
	new_count = str(counter * per_page)
	if new_count == 0:
		return url
	# substitutes in the counter at the point in the strig.
	new_url = pattern.sub(new_count, url)
	return new_url

def has_link_and_class(tag):
	return tag.has_attr('a') and tag.has_attr(class_='row1')

def find_number_of_pages_or_topics(url):
	"""For a given forum or topic it pulls out the number of pages that need to be spidered."""
	#should really be refactored so that it's a single function that identifies whether or not you're on an individual forums page or not.
	# pulls in the soup. should probably refactor this so it's not done twice.
	soup = download(url)

	# pulls in the things that have the class they are using for the tag.
	tags = soup.find_all(class_='gensmall')
	tags = [tag.get_text() for tag in tags]

	# does a regex over their tags to find the number of pages using the format they usually use. 
	for tag in tags:

		if re.findall(r'\[\s([0-9]+)\stopic', tag):
			number_of_topics = re.findall(r'\[\s([0-9]+)', tag)
			number_of_pages = math.ceil(int(number_of_topics[0]) / 50)

		elif re.findall(r'\[\s([0-9]+\spost)', tag):
			number_of_posts = re.findall(r'\[\s([0-9]+)', tag)
			number_of_pages = math.ceil(int(number_of_posts[0]) / 15)
	
	return number_of_pages

def scrape_topic(topic_url):
	"""scrapes all posts from a topic"""
	topic_posts =[]
	counter = 0
	num_pages = find_number_of_pages_or_topics(topic_url)

	# assigns the forum urls start
	url = topic_url + '&start=0'

	#scrapes the posts for each page in the forum.
	while counter < num_pages:
		url = paginator(url, counter, 15)
		posts = scrape_posts(url)
		for post in posts:
			topic_posts.append(post)
		counter += 1

	return topic_posts

def get_all_topic_links_in_a_forum(forum_url):
	"""gets all the topic links in a forum."""
	links = []
	counter = 0
	num_pages = find_number_of_pages_or_topics(forum_url)
	
	url = forum_url + '&t='

	while counter < num_pages:
		url = paginator(url, counter, 50)
		page_links = get_topic_links_for_a_page(forum_url)
		for link in page_links:
			links.append(link)
		counter += 1

	return(links)
	

def get_topic_links_for_a_page(forum_url):
	"""Gets all of the links for the topics contained in a forum."""
	# note: it only does this for one page. You need to paginate
	raw_links = []
	soup = download(forum_url)
	clean_links = []

	# pulls in all the raw links with the topic title class.
	first_round = soup.find_all(class_='topictitle')
	for link in first_round:
		raw_links.append(link.get('href'))

	#cuts out the extraneous information from the topic link and reformats it to be a proper url.
	beginning_pattern = re.compile(r'^\.')
	end_pattern = re.compile(r'&sid=.+$')
	for link in raw_links:
		new_link = end_pattern.sub('', link)
		new_link = beginning_pattern.sub('https://forum.librivox.org', new_link)
		clean_links.append(new_link)
	return clean_links



def scrape_forum(forum_url):
	forum_posts = []
	forum_links = get_all_topic_links_in_a_forum(forum_url)
	for link in forum_links:
		posts = scrape_topic(link)
		for post in posts:
			forum_posts.append(post)
	return forum_posts

scrape_forum('https://forum.librivox.org/viewforum.php?f=18')


