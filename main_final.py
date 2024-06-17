import json
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options   
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
import urllib.parse
from pyvirtualdisplay import Display
from PIL import Image
import logging

app = Flask(__name__)

chrome_options = Options()
# firefox_options = Options()
chrome_options.binary_location = "/usr/bin/google-chrome"  # Path to your Chrome binary
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/scrape_jobs/<position>/<city>/<int:num_listings>/', defaults={'filter_criteria': ''}, methods=['GET'])
@app.route('/scrape_jobs/<position>/<city>/<int:num_listings>/<filter_criteria>', methods=['GET'])
def scrape_jobs(position, city, num_listings, filter_criteria):
    setup_logging()
    start_time = time.time()

    display = None
    try:
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        print("Virtual display started successfully.")
    except Exception as e:
        logging.error(f"Error starting virtual display: {e}")
        print(f"Error starting virtual display: {e}")



    # Construct the search query URL
    search_query = f"{position} in {city} + {filter_criteria}"
    search_query_encoded = urllib.parse.quote(search_query)
    url = f"https://www.google.com/search?q={search_query_encoded}&oq={search_query_encoded}&ibp=htl;jobs&sa=X&fpstate=tldetail"

    # Initialize the Chrome WebDriver
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        # driver = webdriver.Firefox(options=firefox_options)

        driver.get(url)
        time.sleep(0.8)
        
             # Capture screenshot of the virtual display
        screenshot_path = '/tmp/screenshot.png'
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved at {screenshot_path}")
  # Adding delay for the website to load

        final_data = []
        urls = set()

        # Helper function to capture job listings
        def capture_jobs():
            logging.info(f"Capturing job listings... Current count: {len(final_data)}")
            source = driver.page_source
            soup = BeautifulSoup(source, 'html.parser')
            job_cards = soup.find_all("div", class_="oNwCmf")
            
            try:
                for job_card in job_cards:
                    job_info = {}
                    # job_card.click()
                    # job__url  = driver.url
                    # job_info['url'] = job__url
                    company_div = job_card.find("div", class_="vNEEBe")
                    location_div = job_card.find_all("div", class_="Qk80Jf")[0]
                    source_div = job_card.find_all("div", class_="Qk80Jf")[1]
                    other_details = job_card.find_all("div", class_="LL4CDc");
                    posted_date_span = job_card.find("span", aria_label=lambda x: x and "Posted" in x)
                    salary_span = job_card.find("span", aria_label=lambda x: x and "Salary" in x)
                    # employment_type_span = job_card.find("span", aria_label=lambda x: x and "Employment type" in x)
                    temp_cards = job_card.find_all("div", class_="KKh3md")
                    other = job_card.find("div", class_="KKh3md")

                    aria_labels = []
                    employment_type = None
                    salary = None
                    posted = None
                    for temp_card in temp_cards:
                        ll4cdc_spans = temp_card.find_all("span", class_="LL4CDc")
                        for span in ll4cdc_spans:
                            aria_label = span.get("aria-label", "")
                            aria_labels.append(aria_label)
                            if "Employment type" in aria_label:
                                employment_type = span.text
                            if "Salary" in aria_label:
                                salary = span.text
                            if "days" in aria_label:
                                posted = span.text
                            

                                print("Kuch to hua",employment_type, salary,posted)

                    job_info['company'] = company_div.text if company_div else None
                    job_info['other'] = other.text if other else None
                    job_info['location'] = location_div.text if location_div else None
                    job_info['source'] = source_div.text if source_div else None
                    job_info['posted_date'] = posted if posted else None
                    job_info['salary'] = salary if salary else None
                    job_info['employment_type'] = employment_type if employment_type else None
                    job_info['job_url'] = url

                    final_data.append(job_info)
                    logging.info(f"Captured job: {job_info}")

            except Exception as e:
                logging.error(f"Error capturing job listing: {e}")

        # Scroll and capture more job listings after every few cards
        action = ActionChains(driver)
        last_position = 0
        ln_lj=[]
        lenj = 0
        while lenj < num_listings:
            try:
                logging.info("Scrolling down to load more job listings...")
                datas = driver.find_elements(By.CLASS_NAME, "oNwCmf")
                print("Scrapped scroll",len(datas))
                scroll_origin = ScrollOrigin.from_element(datas[len(datas) - 1])
                action.scroll_from_origin(scroll_origin, 0, 1500).perform()
                logging.info("Scrolling down to load more job listings...",len(datas))
                lenj = len(datas)
                ln_lj.append(lenj)
                if(len(ln_lj)>2):
                    if(ln_lj[-1]==ln_lj[-2] and ln_lj[-3]==ln_lj[-2]):
                        break
                time.sleep(0.6)
            except Exception as e:
                logging.error(f"Exception occurred while scrolling: {e}")
                break
            time.sleep(0.1)
        
        capture_jobs()
        logging.info(f"Total unique job URLs captured: {len(urls)}")
        elapsed_time = time.time() - start_time

        print(f"Elapsed time: {elapsed_time} seconds")
    except Exception as e:
        logging.critical(f"Critical error: {e}")
    finally:
        if driver:
            driver.quit()
        if display:
            display.stop()
            print("Virtual display stopped.")

    # Save the cleaned data to a JSON file
    json_filename = 'job-output.json'
    with open(json_filename, 'w') as json_file:
        json.dump(list(final_data), json_file, indent=4)
    
    logging.info(f"Cleaned job data has been saved to '{json_filename}'")
    logging.info(f"Total number of cleaned job listings found: {len(final_data)}")
       
    #return send_file(screenshot_path, mimetype='image/png', as_attachment=True, download_name='screenshot.png')

    return jsonify(final_data)


# Example usage
if __name__ == '__main__':
        app.run(debug=True,port='7889')