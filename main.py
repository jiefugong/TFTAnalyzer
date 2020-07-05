import argparse
import sys

from processing.preprocessor import ImagePreprocessor
from processing.screenshotter import snapshot_league_window
from parser.parser import LoLChessParser
from lolchess_requester.lolchess_requester import LoLChessRequester

parser = argparse.ArgumentParser()
parser.add_argument("--user", help="The user to query results for")
parser.add_argument("--image", help="Path of full-screen image of the loading screen")
args = parser.parse_args()

all_users = []
if args.user:
	all_users.append(args.user)
else:
	image_path = args.image or snapshot_league_window()
	if not image_path:
		sys.exit(1)
	ip = ImagePreprocessor()
	split_images_by_path = ip.split_image(image_path)
	all_users = ip.retrieve_users_from_image(split_images_by_path)

for user in all_users:
	try:
		resp = LoLChessRequester.make_request_for_user("na", user)
		if resp.status_code == 200:
			parser = LoLChessParser(resp.text)

			# TODO: Have a top level function in the parser for returning all of this data
			compositions = parser.get_recently_played_compositions()
			unit_ratio = parser.get_itemized_unit_ratio()
			item_volume = parser.get_itemized_units_by_volume()
			rank, lp = parser.get_user_rank_and_stats()

			# TODO: Use Log modules
			print ("User rank: {}, current lp: {}".format(rank, lp))
			print ("User {} has these itemization trends:\n".format(user))
			print ("Unit itemization volume:\n{}".format(item_volume))

			# TODO: Rate limit or group the requests to LoLChess together
	except Exception:
		print ("Couldn't make request for user: {}".format(user))
		continue





