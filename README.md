

# Job Scraping Application

This Flask application is designed to scrape job listings from Google Search using Selenium WebDriver and return the data in JSON format.

## Prerequisites

Before running the application, make sure you have the following installed:

- Python 3.x
- Flask
- Selenium WebDriver for Chrome (`chromedriver`)
- Chrome browser

Install Python dependencies using `pip`:

```
pip install flask selenium
pip install -r req.txt
```

Download `chromedriver` suitable for your Chrome version from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads) and ensure it's in your system PATH.

## Setup

1. Clone this repository or download the source code.
2. Install dependencies as mentioned above.
3. Ensure `chromedriver` is executable and accessible.
4. Configure the Chrome options in `app.py` if necessary (e.g., adjust headless mode or other Chrome options).

## Running the Application

1. Open a terminal or command prompt.
2. Navigate to the directory where `app.py` is located.
3. Run the Flask application:

   ```
   python app.py
   ```

   The application will start and listen on port 7889 by default (`http://localhost:7889/`).

## Usage

### Endpoint: `/scrape_jobs/<position>/<city>/<int:num_listings>/<filter_criteria>`

- Replace `<position>` with the job position (e.g., `engineer`).
- Replace `<city>` with the city or location (e.g., `new-york`).
- Replace `<num_listings>` with the number of job listings to retrieve (integer).
- Optionally, provide `<filter_criteria>` to further filter the job search (e.g., `full-time`).

### Example

To scrape 10 job listings for `software engineer` in `new york`:

```
GET http://localhost:7889/scrape_jobs/software%20engineer/new%20york/10/
```

To include a filter criteria (`full-time`):

```
GET http://localhost:7889/scrape_jobs/software%20engineer/new%20york/10/full-time
```

## Response

The application returns a JSON response containing an array of job listing objects with the following fields:

- `url`: URL of the job listing.
- `Role`: Role or title of the job.
- `Company`: Name of the hiring company.
- `Description`: Description of the job.
- `otherdetails`: Additional details about the job.

Example response:

```json
[
  {
    "url": "https://example.com/job1",
    "Role": "Software Engineer",
    "Company": "Example Inc",
    "Description": "This is a description of the job.",
    "otherdetails": ["Full-time", "Location: New York"]
  },
  {
    "url": "https://example.com/job2",
    "Role": "Senior Software Engineer",
    "Company": "Another Company",
    "Description": "Description of another job opportunity.",
    "otherdetails": ["Full-time", "Location: New York"]
  }
]
```

## Notes

- Adjust Chrome options in `app.py` (`chrome_options`) based on your system setup and requirements.
- Ensure proper error handling and logging for production deployments.
- This application is for demonstration purposes and should be used responsibly and in compliance with website terms of service.

---

Feel free to customize the README further based on additional details or specific instructions relevant to your application environment and usage scenarios.