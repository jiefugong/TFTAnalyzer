import requests

BASE_URL = "https://lolchess.gg/profile/{}/{}/{}"

class LoLChessRequester(object):
	@staticmethod
	def make_request_for_user(self, region, user, season="s3.5", page="1"):
		request_url = BASE_URL.format(region, user, season, page)
		return requests.get(request_url)
