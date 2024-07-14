import ctypes

# don't edit these
user32 = ctypes.windll.user32
screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)

# editable
output_file_directory = "output/"  # directory where to save results, empty by default
output_file = "output"  # name to output file
output_file_type = "html"  # extension of output file, only html|txt|docx are supported

image_width = 12  # image width in cm to put in word
window_w = 1000  # chrome window width
window_h = 700  # chrome window height
chrome_driver_path = ""  # path to chromedriver
tesseract_path = ""  # path to tesseract

max_page_load_time = 0  # how much to wait for the page to load its chapter holder, works only with chrome
page_load_check_intervals = 0  # intervals between checking if the page was loaded
sleeping_time = 0.3  # forced sleep time before reading page in case sleep is True in process settings
SCROLL_PAUSE_TIME = 0.5  # pause time for scrolling page in case scroll is True in process settings
MAX_SCROLL_ATTEMPTS = 20  # max page scroll attempts in case scroll is True in process settings
text_delimeter = "###"  # used if tags_used is not None in parser settings
MAX_OPEN_ATTEMPTS = 3  # maximum attempts to open page
accepted_length_diff = 3  # used for similar lines erosion in case clean_equal is True in parser settings
compare_start_ignore = 1  # used for similar lines erosion in case clean_equal is True in parser settings
text_preview_symbols_number = 100  # shows this number of symbols when program asks if to consider page reading successful
stylise_text = True  # no idea what it makes
link_info_part = ['src', 'data-src', 'data-breeze']  # what parts to check inside link tag for the link text
jum_list = ["jum", "jmbl"]  # css classes associated with jumbled text

# default process settings
process_dict_default = {"chrome": False,  # shows if chrome should be used
                        "chrome_undetected": False,  # shows if to use chrome undetected library, works only if chrome is True
                        "scroll": False,  # shows if to scroll page
                        "min_par": 10,  # minimum number of paragraphs to consider it successful
                        "min_len": 1000,  # minimum number of symbols to consider it successful
                        "clearing": False,  # if to clear cookies after finishing, works only if chrome is True
                        "block_screen": False,  # if to expect blocking screen to bypass, works only if chrome is True
                        "input_type": None,  # used if input field to fill, works only if block_screen is True
                        "input_limit": None,  # used if input field to fill, works only if input_type is not None
                        "input_content": None,  # used to fill input field, works only if input_type is not None
                        "button_type": None,  # used if button to press, works only if block_screen is True
                        "button_limit": None,  # used to find button to press, works only if button_type is not None
                        "sleep": False,  # if to sleep between chapters
                        "chrome_dir": "",  # location of chrome directory, works only if chrome is True and chrome_undetected is False
                        "chrome_profile": ""  # name of directory of profile to use inside of chrome_dir, works only if chrome is True and chrome_undetected is False and chrome_dir is not None
                        }
active_process_dicts = {"ranobehub.org": {"chrome": False},
                        "tl.rulate.ru": {"chrome": True, "min_len": 2000, "block_screen": True, "button_type": "",
                                         "button_limit": {"name": "ok"}},
                        "www.wattpad.com": {"chrome": True, "scroll": True, "min_par": 1},
                        "www.readlightnovel.me": {"chrome": False},
                        "www.mtlnovel.com": {"chrome": True, "clearing": True, "sleep": True}}

parser_dict_default = {"left": 0,  # number of text paragraphs to exclude at the beginning of each chapter
                       "right": 0,  # number of text paragraphs to exclude at the end of each chapter
                       "text_h": "p",  # html container of text
                       "text_l": None,  # limit for finding text, applied to text_container
                       "text_container": "div",  # html container in which all the text is
                       "text_intelligent": False,  # if to read text using image recognition when it is jummed
                       "text_lang": None,  # expected text language, works if text_intelligent is True
                       "title_h": "title",  # html tag of title or special enum - "title" = use page title - "empty" = don't put it
                       "title_l": None,  # limit for finding title, applied to title_container if not None, else to title_h
                       "title_p": 0,  # which html tag to use out of the list of the ones found
                       "title_container": None,  # html tag in which to search for title
                       "link_h": "a",  # html tag of link
                       "link_l": None,  # limit for finding link, applied to link_container if not None, else to link_h
                       "link_p": 0,  # which html tag to use out of the list of the ones found
                       "link_container": None,  # html tag in which to search for link
                       "clean_equal": True,  # if to clean equal lines
                       "clean_empty": True,  # if to clean empty lines
                       "tags_used": None,  # if to break text of paragraphs using tags instead, give here a list of tags to separate with
                       "images": False,  # if to expect and parse images that are inside text_container, requires output file extension to be html or docs
                       "left_image": 0,  # number of images to exclude at the beginning of each chapter
                       "right_image": 0,  # number of images to exclude at the end of each chapter
                       "put_intelligent": True  # if to put text + images in the order using their place in html page
                       }
# some settings, a few are outdated, a few use outdated set of settings
active_parser_dicts = {"ranobehub.org": {"left": 0, "right": 4,
                                         "text_h": "p", "text_l": None,
                                         "title_h": "title", "title_l": None,
                                         "link_h": "a", "link_l": {'data-hotkey': 'right'}},
                       "tl.rulate.ru": {"left": 0, "right": 1,
                                        "text_h": "p", "text_l": {"class": "content-text"},
                                        "title_h": "title",
                                        "link_h": "a", "link_l": {'class': 'next'}, "link_p": 0, "link_container": 'li'},
                       "www.wattpad.com": {"left": 0, "right": 0,
                                           "text_h": "p", "text_l": {"class", "part-content"}, "text_container": "div",
                                           "title_h": "h1", "title_l": {"class", "h2"},
                                           "link_h": "a", "link_l": {'id': 'story-part-navigation'}, "link_container": "div"},
                       "www.readlightnovel.me": {"left": 1, "right": 0,
                                                 "text_h": "p", "text_l": {"class": "desc"},
                                                 "title_h": "title", "title_l": None,
                                                 "link_h": "a", "link_l": {"class": "next next-link"}},
                       "www.mtlnovel.com": {"left": 0, "right": 0,
                                            "text_h": "p", "text_l": None,
                                            "title_h": "h1", "title_l": None,
                                            "link_h": "a", "link_l": {"class": "next"}}}
