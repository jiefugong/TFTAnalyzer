### TFT Scraper
A tool used to provide insight into your active TFT game. More details to come later.

#### Usage
TODO: Commands should not directly call main.py in the future. Need to package project
`python main.py --user <username>` -> Creates a request and analyzes basic data for one user
`python main.py --image <path/to/image>` -> Given a path to a loading screen image, analyzes all players
`python main.py` -> Attempts to screenshot an active LoL Loading Screen Window (Mac OSX only, for now)

#### TO-DO

- Add MyPy support
- Support & test Windows
- Bundle package dependencies
    - BeautifulSoup4
    - Requests
    - Quartz
    - OpenCV
    - Tesseract
    - Python Imaging Library
- Brew / Pip install support
- Replace prints with log statements
- Write results to external document / PDF, pretty format text
- Riot Games API
    - Storing API key
    - Replacing Web Scraping module with API module
- Print data in a prettier format
    - https://stackoverflow.com/questions/9535954/printing-lists-as-tabular-data
- Better analyze TFT data
    - Categorize player into category (flex, one-trick)
    - Provide immediate insight into how to counter the player