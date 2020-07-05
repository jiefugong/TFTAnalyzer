import os
import platform

from uuid import uuid4
from Quartz import CGWindowListCopyWindowInfo, kCGNullWindowID, kCGWindowListOptionAll

# TODO:
# https://www.reddit.com/r/learnpython/comments/9f4lls/how_to_take_a_screenshot_of_a_specific_window/
# https://stackoverflow.com/questions/19695214/python-screenshot-of-inactive-window-printwindow-win32gui?noredirect=1&lq=1

MAC_LEAGUE_CLIENT_WINDOW_NAME = 'League of Legends (TM) Client'

def generate_filename():
    return str(uuid4())[-10:] + '.png'

def snapshot_league_window():
    """
    Attempts to find an active LoL client window and screenshot it using the appropriate
    functions given the computer architecture. Expects to be called during the loading screen
    to a TFT game otherwise the snapshot produced will not work later.

    Currently expects either Mac OS X or Windows

    :return:
    """
    is_osx = platform.system() == 'Darwin'

    if is_osx:
        window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
        for window in window_list:
            try:
                window_name = window['kCGWindowName']
                if window_name == MAC_LEAGUE_CLIENT_WINDOW_NAME:
                    filename = generate_filename()
                    os.system('screencapture -l %s %s' % (window['kCGWindowNumber'], filename))
                    return filename
            except KeyError:
                continue

        print ("Could not find active LoL client -- are you in the loading screen?")
        return ""
