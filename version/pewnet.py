﻿"""
This file is part of Happypanda.
Happypanda is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
any later version.
Happypanda is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Happypanda.  If not, see <http://www.gnu.org/licenses/>.
"""

import requests, logging, random, time, pickle, os
import re as regex
from bs4 import BeautifulSoup
from datetime import datetime
from .gui import gui_constants

log = logging.getLogger(__name__)
log_i = log.info
log_d = log.debug
log_w = log.warning
log_e = log.error
log_c = log.critical

web_session = requests.Session()
if os.path.isfile(gui_constants.SESSION_COOKIES_PATH):
	with open(gui_constants.SESSION_COOKIES_PATH, 'rb') as f:
		try:
			cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
			if cookies:
				web_session.cookies = cookies
		except EOFError:
			pass
else:
	with open(gui_constants.SESSION_COOKIES_PATH, 'x') as f:
		pass

class CommenHen:
	"Contains common methods"
	LOCK = [False]
	SESSION = web_session
	TIME_RAND = gui_constants.GLOBAL_EHEN_TIME
	QUEUE = []

	@staticmethod
	def hash_search(g_hash):
		"""
		Searches ex or g.e for a gallery with the hash value
		Return list with titles of galleries found.
		"""
		pass

	def begin_lock(self):
		self.LOCK[0] = True
	
	def end_lock(self):
		self.LOCK[0] = False

	def add_to_queue(self, url):
		"Add url the the queue, when the queue has reached 25 entries will auto process"
		self.QUEUE.append(url)
		if len(self.QUEUE) > 24:
			self.process_queue()

	def process_queue(self):
		"""
		Process the queue if entries exists, deletes entries.
		Note: Will only process 25 entries (first come first out) while
			additional entries will get deleted.
		"""
		if len(self.QUEUE) < 1:
			return None

		if gui_constants.FETCH_METADATA_API:
			if len(self.QUEUE > 25):
				self.get_metadata(self.QUEUE[:25])
			else:
				self.get_metadata(self.QUEUE)

		self.QUEUE.clear()

	def check_cookie(self, cookie):
		assert isinstance(cookie, dict)
		print('your cookies', cookie)
		cookies = self.SESSION.cookies.keys()
		print('session cookies', cookies)
		present = []
		for c in cookie:
			if c in cookies:
				present.append(True)
			else:
				present.append(False)
		if not all(present):
			print('Updating cookies')
			self.SESSION.cookies.update(cookie)

	def lock(self, sleep=False):
		while self.LOCK[0]:
			time.sleep(0.1)
		if sleep:
			r_time = random.randint(5,5+self.TIME_RAND)
			time.sleep(r_time)

	def parse_url(self, url):
		"Parses url into a list of gallery id and token"
		gallery_id = int(regex.search('(\d+)(?=\S{4,})', url).group())
		gallery_token = regex.search('(?<=\d/)(\S+)(?=/$)', url).group()
		parsed_url = [gallery_id, gallery_token]
		return parsed_url

	def parse_metadata(self, metadata_json, dict_metadata=None):

		def invalid_token_check(g_dict):
			if 'error' in g_dict:
				return False
			else: return True

		if dict_metadata:
			parsed_metadata = {}
		else:
			parsed_metadata = []

		for gallery in metadata_json['gmetadata']:
			if invalid_token_check(gallery):
				if not dict_metadata:
					parsed_metadata.append(gallery)
				else:
					url = dict_metadata[gallery['gid']]
					parsed_metadata[url] = gallery

		return parsed_metadata

	def get_metadata(self, list_of_urls, cookies=None):
		"""
		Fetches the metadata from the provided list of urls
		through the official API.
		If the povided list of urls contains more than 1 url,
		a dict will be returned with url as key and tags as value
		"""
		assert isinstance(list_of_urls, list)
		if len(list_of_urls) >= 25:
			return None

		payload = {"method": "gdata",
			 "gidlist": []
			 }
		dict_metadata = {}
		if len(list_of_urls) > 1:
			for url in list_of_urls:
				parsed_url = self.parse_url(url.strip())
				dict_metadata[parsed_url[1]] = url # gallery id
				payload['gidlist'].append(parsed_url)
		else:
			parsed_url = self.parse_url(list_of_urls[0].strip())
			payload['gidlist'].append(parsed_url)

		if payload['gidlist']:
			self.lock()
			self.begin_lock()
			if cookies:
				self.check_cookie(cookies)
			r = self.SESSION.post(self.e_url, json=payload)
		else: return None
		try:
			r.raise_for_status()
		except:
			log.exception('Could not fetch metadata')
			return None
		if dict_metadata:
			metdata = self.parse_metadata(r.json(), dict_metadata)
		else:
			metadata = self.parse_metadata(r.json())
		return metadata

	def eh_hash_search(self, hash_string):
		"""
		Searches ehentai for the provided string or list of hashes,
		returns a dict with hash:[list of title:url] of hits found or None if no hits are found.
		"""
		assert isinstance(hash_string, str) or isinstance(hash_search, list)
		if isinstance(hash_string, str):
			hash_string = [hash_string]

		def no_hits_found_check(html):
			"return true if hits are found"
			soup = BeautifulSoup(html)
			f_div = soup.body.find('div')
			if 'No hits found' in f_div.text[-20:]:
				return False
			return True

		hash_url = gui_constants.DEFAULT_EHEN_URL + '?f_shash='
		found_galleries = {}
		for h in hash_string:
			self.lock(sleep=True)
			self.begin_lock()
			r = requests.get(hash_url+h)
			if not no_hits_found_check(r.text):
				continue
			soup = BeautifulSoup(r.text)
			if soup.body:
				found_galleries[h] = []
				# list view or grid view
				type = soup.find(attrs={'class':'itg'}).name
				if type == 'div':
					visible_galleries = soup.find_all('div', attrs={'class':'id1'})
				elif type == 'table':
					visible_galleries = soup.find_all('div', attrs={'class':'it5'})
				
				for gallery in visible_galleries:
					title = gallery.text
					g_url = gallery.a.attrs['href']
					found_galleries[h].append({title:g_url})
			self.end_lock()

		if found_galleries:
			return found_galleries
		else:
			return None

	def eh_gallery_parser(self, url, cookies=None):
		"""
		Parses an ehentai page for metadata.
		Returns gallery dict with following metadata:
		- type
		- language
		- publication date
		- namespace & tags
		"""
		self.lock()
		self.begin_lock()
		if cookies:
			self.check_cookie(cookies)
		r = self.SESSION.get(url, timeout=30)
		html = r.text
		if len(html)<5000:
			log_w("Length of HTML response is only {} => Failure".format(len(html)))
			return {}

		gallery = {}
		soup = BeautifulSoup(html)
		with open('html2.html', 'w', encoding='utf-8') as f:
			f.write(soup.prettify())
		# Type
		div_gd3 = soup.body.find('div', id='gd3')
		gallery['type'] = div_gd3.find('img').get('alt')

		# corrects name
		if gallery['type'] == 'artistcg':
			gallery['type'] = 'artist cg sets'
		elif gallery['type'] == 'imageset':
			gallery['type'] = 'image sets'
		elif gallery['type'] == 'gamecg':
			gallery['type'] = 'game cg sets'
		elif gallery['type'] == 'asianporn':
			gallery['type'] = 'asian porn'

		# Language
		lang_tag = soup.find('td', text='Language:').next_sibling
		lang = lang_tag.text.split(' ')[0]
		gallery['language'] = lang

		# Publication date
		pub_tag = soup.find('td', text='Posted:').next_sibling
		pub_date = datetime.strptime(pub_tag.text.split(' ')[0], '%Y-%m-%d').date()
		gallery['published'] = pub_date

		# Namespace & Tags
		found_tags = {}
		def tags_in_ns(tags):
			return not tags.has_attr('class')
		tag_table = soup.find('div', id='taglist').next_element
		namespaces = tag_table.find_all('tr')
		for ns in namespaces:
			namespace = ns.next_element.text.replace(':', '')
			found_tags[namespace] = []
			tags = ns.find(tags_in_ns).find_all('div')
			for tag in tags:
				found_tags[namespace].append(tag.text)

		gallery['tags'] = found_tags
		return gallery

class ExHen(CommenHen):
	"Fetches galleries from exhen"
	def __init__(self, cookie_member_id, cookie_pass_hash):
		self.cookies = {'ipb_member_id':cookie_member_id,
				  'ipb_pass_hash':cookie_pass_hash}
		self.e_url = "http://exhentai.org/api.php"

	def get_metadata(self, list_of_urls):
		return super().get_metadata(list_of_urls, self.cookies)

	def eh_gallery_parser(self, url):
		return super().eh_gallery_parser(url, self.cookies)

class EHen(CommenHen):
	"Fetches galleries from ehen"
	def __init__(self):
		self.e_url = "http://g.e-hentai.org/api.php"

