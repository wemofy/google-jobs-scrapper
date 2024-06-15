import json
from flask import Flask, request, jsonify
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
import urllib.parse
import logging

app = Flask(__name__)

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
        driver = webdriver.Chrome()
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
                    # time.sleep(0.1)
                    data.click()
                    # time.sleep(0.1)
                    
                    p_e = driver.find_element(By.CSS_SELECTOR, '.EDblX.kjqWgb')
                    eles = driver.find_elements(By.CSS_SELECTOR, '.EDblX.kjqWgb')
                    for ele in eles:
                        url = ele.find_element(By.TAG_NAME, 'a')
                        link = url.get_attribute('href')
                        if ele.get_attribute("jsname") == "s2gQvd" and link not in urls:
                            p_e = ele
                            break

                    url = p_e.find_element(By.TAG_NAME, 'a')
                    exd = {"url": url.get_attribute('href')}
                    urls.add(exd["url"])

                    kk3 = data.find_element(By.CLASS_NAME, 'KKh3md').text
                    des = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/div/div/div[3]/div[2]/div/div[1]/div/div').text

                    details = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/div/div/div[3]/div[2]/div/div[1]/div/div').text.split('\n')

                    exd['Role'] = details[0] if len(details) > 1 else ''
                    exd['Company'] = details[2] + ' ' + details[3] if len(details) > 2 else ''
                    exd['Description'] = des
                    # exd['location'] = details[3] if len(details) > 2 else ''
                    # exd['Full / Part Time'] = details[5] if len(details) > 5 else ''
                    exd['otherdetails'] = kk3.split('\n')
                    

                    final_data.append(exd)
                except Exception as e:
                    logging.error(f"Error capturing job listing: {e}")

        # Scroll and capture more job listings after every few cards
        action = ActionChains(driver)
        last_position = 0
        lenj = 0
        while lenj < num_listings:
            try:
                logging.info("Scrolling down to load more job listings...")
                datas = driver.find_elements(By.CLASS_NAME, "oNwCmf")
                scroll_origin = ScrollOrigin.from_element(datas[len(datas) - 1])
                action.scroll_from_origin(scroll_origin, 0, 1500).perform()
                lenj = len(datas)
                time.sleep(0.1)
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

    # Save the cleaned data to a JSON file
    json_filename = 'job-output.json'
    with open(json_filename, 'w') as json_file:
        json.dump(list(final_data), json_file, indent=4)
    
    logging.info(f"Cleaned job data has been saved to '{json_filename}'")
    logging.info(f"Total number of cleaned job listings found: {len(final_data)}")

    return jsonify(final_data)


# Example usage
if __name__ == '__main__':
        app.run(debug=True,port='7889')

