import json
from flask import Flask, request, jsonify
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
import urllib.parse

app = Flask(__name__)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-software-rasterizer')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/scrape_jobs/<position>/<city>/<int:num_listings>/', defaults={'filter_criteria': ''}, methods=['GET'])
@app.route('/scrape_jobs/<position>/<city>/<int:num_listings>/<filter_criteria>', methods=['GET'])
def scrape_jobs(position, city, num_listings, filter_criteria):
    setup_logging()
    start_time = time.time()

    # Construct the search query URL
    search_query = f"{position} in {city} + {filter_criteria}"
    search_query_encoded = urllib.parse.quote(search_query)
    url = f"https://www.google.com/search?q={search_query_encoded}&oq={search_query_encoded}&ibp=htl;jobs&sa=X&fpstate=tldetail"

    # Initialize the Chrome WebDriver
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(0.8)  # Adding delay for the website to load

        final_data = []
        urls = set()

        # Helper function to capture job listings
        def capture_jobs():
            logging.info(f"Capturing job listings... Current count: {len(final_data)}")
            datas = driver.find_elements(By.CLASS_NAME, "oNwCmf")

            for data in datas:
                if len(final_data) >= num_listings:
                    break

                try:
                    driver.execute_script("arguments[0].scrollIntoView();", data)
                    data.click()

                    p_e = driver.find_element(By.CSS_SELECTOR, '.EDblX.kjqWgb')
                    url = p_e.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    if p_e.get_attribute("jsname") == "s2gQvd" and url not in urls:
                        des = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/div/div/div[3]/div[2]/div/div[1]/div/div').text
                        kk3 = data.find_element(By.CLASS_NAME, 'KKh3md').text
                        details = des.split('\n')

                        exd = {
                            "url": url,
                            "Role": details[0] if len(details) > 1 else '',
                            "Company": details[2] + ' ' + details[3] if len(details) > 2 else '',
                            "Description": des,
                            "otherdetails": kk3.split('\n')
                        }
                        final_data.append(exd)
                        urls.add(url)
                except Exception as e:
                    logging.error(f"Error capturing job listing: {e}")

        # Scroll and capture more job listings
        action = ActionChains(driver)
        lenj = 0
        while lenj < num_listings:
            try:
                datas = driver.find_elements(By.CLASS_NAME, "oNwCmf")
                if datas:
                    scroll_origin = ScrollOrigin.from_element(datas[-1])
                    action.scroll_from_origin(scroll_origin, 0, 1500).perform()
                    lenj = len(datas)
                    time.sleep(0.1)
                else:
                    break
            except Exception as e:
                logging.error(f"Exception occurred while scrolling: {e}")
                break
            time.sleep(0.1)

        capture_jobs()
        logging.info(f"Total unique job URLs captured: {len(urls)}")
        elapsed_time = time.time() - start_time
        logging.info(f"Elapsed time: {elapsed_time} seconds")

    except Exception as e:
        logging.critical(f"Critical error: {e}")
    finally:
        if driver:
            driver.quit()

    # Save the cleaned data to a JSON file
    json_filename = 'job-output.json'
    with open(json_filename, 'w') as json_file:
        json.dump(list(final_data), json_file, indent=4)
    
    logging.info(f"Cleaned job data has been saved to '{json_filename}'")
    logging.info(f"Total number of cleaned job listings found: {len(final_data)}")

    return jsonify(final_data)

# Example usage
if __name__ == '__main__':
    app.run(debug=True, port=7889)
