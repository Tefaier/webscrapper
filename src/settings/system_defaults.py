from datetime import timedelta

CHROME_DRIVER_PATH = "C:/Users/timab/Downloads/chromedriver-win64/chromedriver.exe"  # path to chromedriver
TESSERACT_PATH = "C:/Program Files/Tesseract-OCR/tesseract.exe"  # path to tesseract
OUTPUT_FILE_DIRECTORY = "C:/Users/timab/PycharmProjects/webscrapper/temp/output/"
CHROME_DIRECTORY = "C:/Users/timab/PycharmProjects/webscrapper/dependencies/selenium_chrome"
CHROME_PROFILE = "Default"  # not supported - Default will be forcefully used
TEMP_FOLDER = "C:/Users/timab/PycharmProjects/webscrapper/temp"
DB_PATH = "C:/Users/timab/PycharmProjects/webscrapper/db/app.db"
WINDOW_W_MIN = 400
WINDOW_W_MAX = 1920
WINDOW_H_MIN = 400
WINDOW_H_MAX = 2000
MAX_NEW_WEBSITE_REQUESTS = 100
MAX_ACTIVE_PROCESSES = 10
MAX_CHAPTERS_COUNT = 300
TASKS_EXECUTION_TIMEOUT_SECONDS = 900
FINISHED_TASKS_LIFETIME = timedelta(days=2)
APPLICATION_LOGS_PATH = "C:/Users/timab/PycharmProjects/webscrapper/temp/app_log.txt"
