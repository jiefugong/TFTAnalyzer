import os

from screenshotter import generate_filename

import cv2
import numpy as np
import pytesseract
from PIL import Image

class ImagePreprocessor(object):

    def __init__(self, clean_assets=True):
        """
        Each element in split_dimensions is a tuple where the first two elements
        are the x,y coords for the top left corner to crop, followed by the bottom right

        They were determined based on a full-screen image of a loading screen which
        gave an image resolution of 3584x2240. We may need to determine the resolution
        of the input image, and scale it to this resolution before attempting text
        extraction to make this more scalable.
        """
        self.split_dimensions = [
            (754, 1012, 1044, 1050),
            (1350, 1012, 1640, 1050),
            (1946, 1012, 2238, 1050),
            (2546, 1012, 2836, 1050),
            (754, 2130, 1044, 2168),
            (1350, 2130, 1640, 2168),
            (1946, 2130, 2238, 2168),
            (2546, 2130, 2836, 2168),
        ]
        self.intermediate_assets = []
        self.clean_assets = clean_assets

    def __del__(self):
        if self.clean_assets:
            for asset in self.intermediate_assets:
                try:
                    os.remove(asset)
                except OSError:
                    print ("Could not find asset {} to delete".format(asset))
                    continue

    def split_image(self, image_path):
        """
        Takes in the initial loading screen image, and splits it into the
        8 quadrants in order to process all of the usernames. Coordinates
        used to split the images are pre-calculated

        :param image_path:
        :return: A list of paths where the cropped images were saved
        """
        result_paths = []
        img = Image.open(image_path)
        for idx, area in enumerate(self.split_dimensions):
            cropped_img = img.crop(area)
            file_name = "{}/{}.png".format(os.getcwd(), "user_{}".format(idx))
            cropped_img.save(file_name)
            result_paths.append(file_name)
            self.intermediate_assets.append(file_name)
        return result_paths

    def retrieve_users_from_image(self, image_paths):
        """
        Take in a list of input images, and preprocess them using
        OpenCV. The output images will be grayscale and ready for
        text analysis using Tesseract

        :param image_paths:
        :return:
        """
        users = [None for _ in range(len(image_paths))]
        for idx, path in enumerate(image_paths):
            curr_img = cv2.imread(path)
            curr_img = self._apply_filters(curr_img)
            text = pytesseract.image_to_string(curr_img, lang="eng")
            users[idx] = text
        return users

    def rescale_image(self, image_path):
        """
        Takes in an input image and rescales it to 3584x2220
        :param image_paths:
        :return:
        """
        filename = generate_filename()
        width, height = 3584, 2220
        img = Image.open(image_path)
        img = img.resize((width, height), Image.ANTIALIAS)
        img.save(filename)
        self.intermediate_assets.append(filename)
        return filename

    def _apply_filters(self, image):
        """
        Apply a number of preset filters to the image such as greyscale
        conversion, blurring, etc. More details found from:
        https://medium.com/free-code-camp/getting-started-with-tesseract-part-ii-f7f9a0899b3f

        :param image:
        :return:
        """
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.dilate(image, kernel, iterations=1)
        image = cv2.erode(image, kernel, iterations=1)
        image = cv2.GaussianBlur(image, (5, 5), 0)
        image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        return image
