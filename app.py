import json
from flask import Flask, request, jsonify, send_file
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
import urllib.parse
import logging
from pyvirtualdisplay import Display
from PIL import Image
import io

app = Flask(__name__)

chrome_options = Options()
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

    # Initialize virtual display
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
        time.sleep(1)  # Adding delay for the website to load

        # Capture screenshot of the virtual display
        screenshot_path = '/tmp/screenshot.png'
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved at {screenshot_path}")

        final_data = []
        urls = set()

        # Helper function to capture job listings
        def capture_jobs():
            logging.info(f"Capturing job listings... Current count: {len(final_data)}")
            datas = driver.find_elements(By.CLASS_NAME, "oNwCmf")
            
            for data in datas:
                if len(final_data) >= num_listings:
                    break
#			time.sleep(0.4)	
                try:
                    driver.execute_script("arguments[0].scrollIntoView();", data)
                    data.click()

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
		#logging.info("Scroll Completed",len(datas))
                datas = driver.find_elements(By.CLASS_NAME, "oNwCmf")
                scroll_origin = ScrollOrigin.from_element(datas[len(datas) - 1])
                action.scroll_from_origin(scroll_origin, 0, 1500).perform()
                lenj = len(datas)
		    #print(lenj)
                time.sleep(0.1)
          	#logging.info("Scroll completed. Number of job cards:"len(datas))
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

    # Return the screenshot as a downloadable file
    #return send_file(screenshot_path, mimetype='image/png', as_attachment=True, download_name='screenshot.png')
    return jsonify(final_data)
# Example usage
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port='7889')