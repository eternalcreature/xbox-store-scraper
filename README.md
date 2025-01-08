# xbox store scraper
 
## What it does?

The script pulls selected metadata from the xbox.com store listings.

## How it works?

It loads the list of urls contained in the url.txt file. For each link, it pulls information about the title, its capabilities and its platforms. It then compares it to the data previously saved in the database. If it's the first time the title is being added, it's logged as:

"Added the entry for {title}."

If the title had already been added to the database and some of the information has changed, the script logs the changes and overwrites the previous entry in the database. If there are no changes, nothing is being done to keep the log files as concise as possible.

The changes are logged in txt files under:
/logs/log_YYYY_MM_DD-HH_MM_SS.txt

Additionally, if the script is run from the xbox_scraper.ipynb notebook, it generates color coded tables, first for the new or updated entries only, then for the entire database.

## How to use it?
Either run the main.py file in your python environment or the xbox_scraper.ipynb notebook. 

The script *should* work with any Python version from 3.8 onwards (written on 3.12, not tested otherwise) and the required modules are listed in the requirements.txt file (run the command ```pip install -r requirements.txt```).

To get new entries to the database, simply add new urls in the urls.txt file and save it before running the script again. 

You can browse the stored metadata in the data.yaml file.

You can check the changes to the database by browsing the /logs folder.

To get the color coded tables, the script must be run from the Jupyter notebook xbox_scraper.ipynb.

Color coding descriptions:
- grey - the game is not listed as Play Anywhere, listed only for PC or only console
- red - the game is listed as Play Anywhere but listed only for PC or only for console
- orange - the game is not listed as Play Anywhere but listed for both console and PC
- green - the game is listed as Play Anywhere and listed for both console and PC

# Peculiarity

YAML is used to store the data. If the game title has a colon ':' or several other special signs, the entry is stored with apostrophies, otherwise it's just the raw title. Because of that, the database after sorting lists first all the titles with the special signs, then the titles without them in alphabetical order.