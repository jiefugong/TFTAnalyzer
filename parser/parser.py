import sys

from collections import defaultdict

from bs4 import BeautifulSoup

class LoLChessParser(object):

	def __init__(self, html):
		self.soup = BeautifulSoup(html, features="lxml")
		self.itemized_units = defaultdict(int)
		self.itemized_unit_matches = defaultdict(int)
		self.trait_history = defaultdict(int)

		try:
			self.match_history = self._retrieve_match_history(self.soup)
			self.profile = self._retrieve_profile_info(self.soup)
			self.scores = self._retrieve_profile_scores(self.soup)
		except AssertionError as err:
			print ("Could not retrieve data: {}".format(err))
			sys.exit(1)

		self._populate_unit_item_history()

	def get_user_rank_and_stats(self):
		"""
		Retrieve the user's current rank and other stats including win rate,
		top 4 rate, and average rank
		"""
		profile = self.profile[0]
		rank = profile.find("span", {"class": "profile__tier__summary__tier"}).text
		current_lp = profile.find("span", {"class": "profile__tier__summary__lp"}).text
		return rank, current_lp

	def get_recently_played_compositions(self):
		"""
		We should evaluate the soup and look for all of the match history
		items (defaults to 10, handle the case of more than 10 matches later)

		After, we will need to evaluate each item and look for the attributes
		that determine the compositions
		"""
		for match in self.match_history:
			for trait in self._retrieve_traits_from_match(match):
				self.trait_history[trait] += 1

		self.trait_history = sorted(self.trait_history.items(), key = lambda x: x[1])
		self.trait_history.reverse()
		return self.trait_history

	def get_itemized_unit_ratio(self):
		"""
		Tracks played characters and how many times they were given items over the
		games they were played. A higher itemization ratio indicates that the unit
		is heavily utilized as a carry / tank unit.
		"""
		champion_itemization_ratio = {}

		if self.itemized_units and self.itemized_unit_matches:
			for champion in self.itemized_units:
				champion_itemization_ratio[champion] = \
					self.itemized_units[champion] / float(self.itemized_unit_matches[champion])

		champion_itemization_ratio = sorted(champion_itemization_ratio.items(), key = lambda x: x[1])
		champion_itemization_ratio.reverse()
		return champion_itemization_ratio

	def get_itemized_units_by_volume(self):
		"""
		Tracks played characters and the pure raw value of how many items they were given
		"""
		if self.itemized_units:
			sorted_itemized_units = sorted(self.itemized_units.items(), key=lambda x: x[1])
			sorted_itemized_units.reverse()
			frequently_used_units = [unit for unit in sorted_itemized_units if unit[1] >= 3]
			return frequently_used_units
		return []

	def get_match_history_scores(self):
		"""
		Returns the weighted score average from the last 5 games, the number of first place finishes,
		the number of top four finishes, and overall scores in the last 20 games
		"""
		if self.scores:
			average_rank_last_5 = self.scores.find('dl', {'class': 'average-5'}).find('dd').get_text()
			wins_last_20 = self.scores.find('dl', {'class': 'wins'}).find('dd').get_text()
			tops_last_20 = self.scores.find('dl', {'class': 'top'}).find('dd').get_text()
			scores_last_20 = [item.get_text() for item in self.scores.find('ul').findAll('li')]
			score_distribution = defaultdict(int)
			for score in scores_last_20:
				score_distribution[int(score)] += 1
			return average_rank_last_5, wins_last_20, tops_last_20, score_distribution
		return None, None, None, None

	def _populate_unit_item_history(self):
		"""
		Evaluate the match history in order to determine the characters
		that were most frequently itemized
		"""
		for match in self.match_history:
			for champion, num_items in self._retrieve_itemized_units_from_match(match).items():
				self.itemized_units[champion] += num_items
				self.itemized_unit_matches[champion] += 1

	def _retrieve_profile_info(self, soup):
		"""
		Given the soup, find the profile items
		"""
		profile = soup.findAll("div", {"class": "profile__tier"})
		assert(len(profile) > 0)
		return profile

	def _retrieve_match_history(self, soup):
		"""
		Given the soup, find the match history items (probably use a constants file
		in order to store all of the class names; can be done later)
		"""
		match_history = soup.findAll("div", {"class": "profile__match-history-v2__item"})
		assert(len(match_history) > 0)
		return match_history

	def _retrieve_profile_scores(self, soup):
		"""
		Retrieve the average rank, number of top 4 finishes, and overall distribution
		of how well the player scored over the last 20 games
		"""
		placement_history = soup.find("div", {"class": "profile__placements"})
		assert placement_history is not None
		return placement_history

	def _retrieve_traits_from_match(self, match):
		"""
		Given a match, determine what traits were used
		"""
		trait_hexes = match.find_all("div", {"class": "tft-hexagon"})
		traits = [trait_hex.find("img").get("title") for trait_hex in trait_hexes]
		return traits

	def _retrieve_itemized_units_from_match(self, match):
		"""
		Given a match, determine which characters were itemized, sorted
		by the number of items that character had equipped
		"""
		unit_items = {}
		units = match.find_all("div", {"class": "unit"})

		for unit in units:
			champion_name = unit.find("div", {"class": "tft-champion"}).find("img").get("title")
			num_items = len(unit.find("ul", {"class": "items"}).find_all("img"))

			if num_items:
				unit_items[champion_name] = num_items

		return unit_items
