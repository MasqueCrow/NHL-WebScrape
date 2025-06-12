from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium_stealth import stealth
import time
import csv
import json
import random

def load_config(path='config.json'):
	with open(path, 'r') as f:
		return json.load(f)

def get_random_user_agent(user_agents):
	return random.choice(user_agents)


def random_delay(config):
	if config.get('random_delay', False):
		delay = random.uniform(config.get('min_delay', 3), config.get('max_delay', 7))
		time.sleep(delay)

def setup_driver(config):
	options = Options()

	# detach mode, set True for browser to stay open after web scraping completed
	if config.get('use_detach', False):
	    options.add_experimental_option("detach", True)
	else:
	    options.add_experimental_option("detach", False)

	# headless mode, set True to run Chrome in the background without GUI
	if config.get('use_headless', True):
		options.add_argument("--headless=new")  # or "--headless"

	# rotate user agent, anti-scraping measure
	if config.get('rotate_user_agent', False):
		ua = get_random_user_agent(config.get('user_agents', []))
		if ua:
			options.add_argument(f'user-agent={ua}')

	# proxy, anti-scraping measure
	if config.get('use_proxy', False):
		proxy = config.get('proxy')
		if proxy:
			options.add_argument(f'--proxy-server={proxy}')

	# disable JavaScript, anti-scraping measure
	if config.get('disable_javascript', False):
		options.add_experimental_option("prefs", {
			"profile.managed_default_content_settings.javascript": 2
		})

	service = Service('./chromedriver')	
	driver = webdriver.Chrome(service=service, options=options)

	# apply stealth mode if enabled, anti-scraping measure
	if config.get('use_stealth', False):
		stealth(driver,
				languages=["en-US", "en"],
				vendor="Google Inc.",
				platform="Win32",
				webgl_vendor="Intel Inc.",
				renderer="Intel Iris OpenGL Engine",
				fix_hairline=True,
				)

	return driver


def export_data(data, filename, file_format):
    """
    Export a list of dictionaries to a CSV or JSON file.

    :param data: List of dictionaries containing the data to export
    :param filename: Base name of the file (without extension)
    :param file_format: 'csv' or 'json' (default 'csv')
    """
    if not data:
        print("No data to export.")
        return

    if file_format.lower() == 'csv':
        full_filename = f"{filename}.csv"
        headers = data[0].keys()

        with open(full_filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        print(f"Data exported successfully to {full_filename}")

    elif file_format.lower() == 'json':
        full_filename = f"{filename}.json"

        with open(full_filename, mode='w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=4)
        print(f"Data exported successfully to {full_filename}")

    else:
        print(f"Unsupported file format: {file_format}. Please use 'csv' or 'json'.")

def locate_element(driver, selector, selector_type, timeout=5):
	"""
	Locate a single element with a timeout.
	Returns the element if found within timeout, else raises TimeoutException.
	"""
	end_time = time.time() + timeout
	while True:
		try:
			element = driver.find_element(selector_type, selector)
			return element
		except:
			if time.time() > end_time:
				raise TimeoutException(f"Element {selector} not found within {timeout} seconds")
			time.sleep(0.5)

def locate_elements(driver, selector, selector_type, timeout=5):
	"""
	Locate multiple elements with a timeout.
	Returns list of elements if found within timeout, else empty list.
	"""
	end_time = time.time() + timeout
	while True:
		try:
			elements = driver.find_elements(selector_type, selector)
			if elements:
				return elements
		except:
			pass
		if time.time() > end_time:
			return []
		time.sleep(0.5)

def scrape_NHL_data(driver):
	driver.get("https://www.scrapethissite.com/pages/forms/")

	# Change "items per page" dropdown to 100 using By.ID (may fail if no id)
	try:
		per_page_select = locate_element(driver, "per_page", By.ID)
		select = Select(per_page_select)
		select.select_by_value("100")  
		time.sleep(5)  # Wait for page reload after changing per_page
		print("Successfully updated to 100 items per page")
	except TimeoutException:
		print("Could not find per_page dropdown by ID. Continuing with default 25 per page.")

	all_teams = []

	while True:
		# locate all pagination links 
		pagination_links = locate_elements(driver, "ul.pagination li a", By.CSS_SELECTOR)
		page_tracker = set()

		for i in range(len(pagination_links)):
			#Re-locate pagination links to avoid old reference error after DOM refresh
			pagination_links = locate_elements(driver, "ul.pagination li a", By.CSS_SELECTOR)	
			page_number = pagination_links[i].text.strip()

			if page_number not in page_tracker:
				page_tracker.add(page_number)
				print(f"On page {page_number}, extracting data...")

				if page_number != "1":					
					try:
						print(f"Clicking page {page_number}")
						pagination_links[i].click()
						time.sleep(3)  # Wait for page to load after click
						

					except Exception as e:
						print(f"Failed to click page {page_number}: {e}")
						continue

				try:
					# retrieve all table rows in current page
					rows = locate_elements(driver, "table.table tbody tr.team", By.CSS_SELECTOR)
					if not rows:
						print("No table rows found, ending scrape.")
						return

					print(f"{len(rows)} rows found on page {page_number}")

					for row in rows:
						cells = row.find_elements(By.TAG_NAME, "td")
						team_data = {
							"Team Name": cells[0].text,
							"Year": cells[1].text,
							"Wins": cells[2].text,
							"Losses": cells[3].text,
							"OT Losses": cells[4].text,
							"Win %": cells[5].text,
							"Goals For (GF)": cells[6].text,
							"Goals Against (GA)": cells[7].text,
							"+ / -": cells[8].text,
						}
						all_teams.append(team_data)

					print(f"Completed extracting data from page {page_number}")
				except TimeoutException:
					print("Timeout while locating table rows, stopping scrape.")
					return
				except NoSuchElementException:
					print("Table rows not found, stopping scrape.")
					return


		# exit loop after web scrape completed
		break
	
	print('=========Sample Data=========')
	print(all_teams[:5])
	print('===================================')
	print("Total no. of data extracted:", len(all_teams))

	#driver.quit()
	return all_teams

if __name__ == "__main__":
	# load config setting and initialise selenium driver 
	config = load_config(path='config.json')
	driver = setup_driver(config)

	# data extraction
	data = scrape_NHL_data(driver)

	# export data in json and csv format
	export_data(data, 'nhl_teams', 'json')
	export_data(data, 'nhl_teams', 'csv')
