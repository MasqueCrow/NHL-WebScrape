
## Run Web Scraper

To start the web scraping process, run `python3 index.py` in the terminal

## Setup

Before running the project, ensure you have the following installed:
 
- **Download project**

  Clone the project in your local machine
   
- **Python 3.7+**  
  Download and install from [python.org](https://www.python.org/downloads/)

- **Google Chrome Browser**  
  Download and install the latest version from [google.com/chrome](https://www.google.com/chrome/)

- **ChromeDriver**  
  The ChromeDriver version must **match with Chrome browser version**.
  Download the appropriate version from [chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads)
  Place the `chromedriver` executable **in project root folder** and ensure it is named exactly `chromedriver` (no file extension)

- **Install Packages**

  Run `pip install -r requirements.txt` in the terminal to install package dependencies
  
## File Overview
**index.py**

This is the main file that performs scraping of [NHL data](https://www.scrapethissite.com/pages/forms/) with Selenium and export the data in json and csv format

**config.json**

This JSON configuration file contains setting to control scaping behavior and helps avoid detecting while interacting with website using Selenium and Chrome.

- **Browser behavior:**  
- `use_detach`: Whether to keep the Chrome browser open after scraping completes  
- `use_headless`: Run Chrome in headless mode (without GUI) if set to `true` 
- `disable_javascript`: Option to disable JavaScript execution in the browser

- **Anti-scraping measures:**  
- `rotate_user_agent`: Enables rotating user-agent strings to mimic different browsers/devices
- `user_agents`: A list of user-agent strings used for rotation  
- `use_proxy` and `proxy`: Optionally route traffic through a proxy server to mask IP address 
- `use_stealth`: Applies stealth techniques to reduce detection by anti-bot systems

- **Request timing:**  
- `random_delay`: Enables random delays between requests to simulate human browsing
- `min_delay` and `max_delay`: Define the range (in seconds) for random delays
