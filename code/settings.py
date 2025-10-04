import ctypes

# don't edit these
user32 = ctypes.windll.user32
screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)

# editable
output_file_directory = "../temp/output/"  # directory where to save results, empty by default
output_file = "output"  # name to output file
output_file_type = "txt"  # extension of output file, only html|txt|docx are supported

image_width = 12  # image width in cm to put in word
window_w = 1920  # chrome window width
window_h = 1080  # chrome window height
chrome_driver_path = "C:/Users/timab/Downloads/chromedriver-win64/chromedriver.exe"  # path to chromedriver
tesseract_path = "C:/Program Files/Tesseract-OCR/tesseract.exe"  # path to tesseract

max_page_load_time = 1  # how much to wait for the page to load its chapter holder, works only with chrome
page_load_check_intervals = 1  # intervals between checking if the page was loaded
sleeping_time = 1  # forced sleep time before reading page in case sleep is True in process settings
wait_before_reading = 4 # 2  # can be used with chrome to parse text only after some time page being opened
SCROLL_PAUSE_TIME = 2 # 0.5  # pause time for scrolling page in case scroll is True in process settings
MAX_SCROLL_ATTEMPTS = 20  # max page scroll attempts in case scroll is True in process settings
text_delimeter = "###"  # used if tags_used is not None in parser settings
MAX_OPEN_ATTEMPTS = 3  # maximum attempts to open page
accepted_length_diff = 3  # used for similar lines erosion in case clean_equal is True in parser settings
compare_start_ignore = 1  # used for similar lines erosion in case clean_equal is True in parser settings
text_preview_symbols_number = 100  # shows this number of symbols when program asks if to consider page reading successful
stylise_text = True  # no idea what it makes
link_info_part = ['src', 'data-src', 'data-breeze']  # what parts to check inside link tag for the link text
jum_list = ["jum", "jmbl"]  # css classes associated with jumbled text
MAX_WAIT_FOR_BUTTON_CLICK_CHANGE = 10

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
                        "wait": False,  # if to wait before reading content
                        "chrome_dir": "C:\\Users\\timab\\PycharmProjects\\webscrapper\\dependencies\\selenium_chrome",  # location of chrome directory, works only if chrome is True and chrome_undetected is False
                        "chrome_profile": "Profile 1",  # name of directory of profile to use inside of chrome_dir, works only if chrome is True and chrome_undetected is False and chrome_dir is not None
                        }
active_process_dicts = {"ranobehub.org": {"chrome": False},
                        "jaomix.ru": {"chrome": False},
                        "ranobes.com": {"chrome": True},
                        "ranobes.net": {"chrome": True, "sleep": True},
                        "ranobelib.me": {"chrome": True, "sleep": True},
                        "tl.rulate.ru": {"chrome": True, "min_len": 2000, "block_screen": True, "button_type": "",
                                         "button_limit": {"name": "ok"}},
                        "www.wattpad.com": {"chrome": True, "scroll": True, "min_par": 1, "wait": True},
                        "www.readlightnovel.me": {"chrome": False},
                        "www.mtlnovel.com": {"chrome": True, "clearing": True, "sleep": True},
                        "www.mtlnovels.com": {}, # {"chrome": True, "clearing": True, "chrome_undetected": True},
                        "18.foxaholic.com": {"chrome": True},
                        "www.foxaholic.com": {"chrome": True},
                        "rainbow-reads.com": {"chrome": False},
                        "danmeiextra.home.blog": {"chrome": False},
                        "younettranslate.com": {"chrome": False},
                        "strictlybromance.com": {"chrome": True},
                        "chrysanthemumgarden.com": {"chrome": True, "chrome_undetected": False, "wait": True},
                        "kinkytranslations.com": {"chrome": False},
                        "www.isotls.com": {"chrome": False},
                        "www.royalroad.com": {"chrome": False},
                        "exiledrebelsscanlations.com": {"chrome": False},
                        "moonlightnovel.com": {"chrome": False},
                        "www.novelcool.com": {"chrome": True},
                        "dummynovels.com": {"chrome": False, "chrome_undetected": True},
                        "www.wuxiaworld.eu": {"chrome": False},
                        "www.wuxiabee.com": {"chrome": True},
                        "www.asianovel.net": {"chrome": True, "sleep": False},
                        "wuxiaworld.ru": {"chrome": False},
                        "huahualibrary.wordpress.com": {},
                        "www.teanovel.com": {},
                        "novelhi.com": {"chrome": True},
                        "novellive.net": {"chrome": True},
                        "www.fansmtl.com": {},
                        "bambootriangle.wordpress.com": {},
                        "whiteskytranslations.wordpress.com": {},
                        "novelbin.englishnovel.net": {},
                        "novelbjn.novelupdates.net": {"chrome": True, "wait": True},
                        "neondragonfly.org": {},
                        "www.lightnovelworld.co": {"chrome": True},
                        "lightnovel.novelcenter.net": {},
                        "secondlifetranslations.com": {"chrome": True},
                        "www.webnovelpub.pro": {"chrome": True, "chrome_undetected": False},
                        "fast.novelupdates.net": {},
                        "ckandawrites.online": {},
                        "knoxt.space": {},
                        "renovels.org": {"chrome": True, "wait": True},
                        "novelbin.com": {"chrome": True},
                        "wuxia.click": {"chrome": True, "sleep": True},
                        "shanghaifantasy.com": {"chrome": True, "wait": True},
                        "novelbin.lanovels.net": {"chrome": True},
                        "m.novel-cat.com": {"chrome": True, "wait": True},
                        "www.goodnovel.com": {},
                        "tapas.io": {"chrome": True, "wait": True},
                        "silver-prince.com": {"chrome": True, "wait": True},
                        "www.novelhall.com": {"chrome": True, "chrome_undetected": False},
                        "ranobes.top": {"chrome": True, "chrome_undetected": True},
                        "www.fanmtl.com": {"chrome": True},
                        "author.today": {"chrome": True, "wait": True},
                        "wtr-lab.com": {"chrome": True},
                        "sleepytranslations.com": {"chrome": True},
                        "www.silknovel.com": {},
                        "loomywoods.com": {"chrome": True},
                        "littlepinkstarfish.com": {},
                        "snowlyme.com": {"chrome": True},
                        "bittercoffeetranslations.com": {"chrome": True, "wait": True},
                        "huitranslation.com": {}}

parser_dict_default = {"left": 0,  # number of text paragraphs to exclude at the beginning of each chapter
                       "right": 0,  # number of text paragraphs to exclude at the end of each chapter
                       "text_h": "p",  # html container of text
                       "text_l": None,  # limit for finding text, applied to text_container
                       "text_container": "div",  # html container in which all the text is
                       "text_intelligent": False,  # if to read text using image recognition when it is jummed and ignore hidden text
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
                       "put_intelligent": True,  # if to put text + images in the order using their place in html page
                       "press_link": True,
                       "link_sleep_and_reload": False,
                       "link_pure_click": False}
# some settings, a few are outdated, a few use outdated set of settings
active_parser_dicts = {"ranobehub.org": {"left": 0, "right": 4,
                                         "text_h": "p", "text_container": None,
                                         "title_h": "h1",
                                         "link_h": "a", "link_l": {'data-hotkey': 'right'}},
                       "jaomix.ru": {"left": 2, "right": 3,
                                     "text_h": "p", "text_l": None,
                                     "title_h": "h1", "title_l": None,
                                     "link_h": "a", "link_l": {'class': 'next'}, "link_p": 0, "link_container": 'li'},
                       "ranobes.com": {"text_h": ["p", "blockquote"], "text_l": {"id": "arrticle"}, # "tags_used": ["br", "div"]
                                       "title_h": "h1",
                                       "link_h": "a", "link_l": {'id': 'next'}},
                       "ranobes.net": {"left": 0, "right": 0,
                                       "text_h": "p", "text_l": None,
                                       "title_h": "title", "title_l": None,
                                       "link_h": "a", "link_l": {'id': 'next'}},
                       "ranobelib.me": {"left": 0, "right": 0, "images": True,
                                        "text_h": "p", "text_l": {"class": "text-content"},
                                        "title_h": "h1",
                                        "link_h": "a", "link_l": {'class': 'wa_p'}, "link_p": -1, "link_container": "div"},
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
                                            "link_h": "a", "link_l": {"class": "next"}},
                       "www.mtlnovels.com": {"left": 0, "right": 0,
                                            "text_h": "p", "text_l": {"class", "par"},
                                            "title_h": "h1", "title_l": None,
                                            "link_h": "a", "link_l": {"class": "next"}},
                       "18.foxaholic.com": {"left": 0, "right": 0,
                                            "text_h": "p", "text_l": {"class": "text-left"},
                                            "title_h": "title", "title_l": None,
                                            "link_h": "a", "link_l": {"class": "next_page"}},
                       "www.foxaholic.com": {"left": 0, "right": 0,
                                             "text_h": "p", "text_l": {"class": "text-left"},
                                             "title_h": "title", "title_l": None,
                                             "link_h": "a", "link_l": {"class": "next_page"}},
                       "rainbow-reads.com": {"left": 0, "right": 1,
                                             "text_h": "p", "text_l": {"class": "post-content"},
                                             "title_h": "h1", "title_l": None,
                                             "link_h": "a", "link_l": {'text': 'Next Page »'}},
                       "danmeiextra.home.blog": {"left": 1, "right": 2,
                                                 "text_h": "p", "text_l": {"class": "entry-content"},
                                                 "title_h": "empty", "title_l": None,
                                                 "link_h": "a", "link_l": {'text': 'Next Chapter'}},
                       "younettranslate.com": {"left": 0, "right": 0,
                                               "text_h": "p", "text_l": {"class": "postdata-content"},
                                               "title_h": "title", "title_l": None,
                                               "link_h": "a", "link_l": {"class": "chapters-navpanel"}, "link_by_div": True, "link_p": -1},
                       "strictlybromance.com": {"left": 1, "right": 1,
                                                "text_h": "p", "text_l": {"class": "post-content"},
                                                "title_h": "title", "title_l": None,
                                                "link_h": "a", "link_l": {"class": "wp-next-post-navi-next"}, "link_by_div": True},
                       "chrysanthemumgarden.com": {"left": 0, "right": 0,
                                                   "text_h": "p", "text_l": {"id": "novel-content"}, "text_intelligent": True, "text_lang": ["eng"],
                                                   "title_h": "title", "title_l": None,
                                                   "link_h": "a", "link_l": {"class": "nav-next"}, "images": True},
                       "kinkytranslations.com": {"left": 1, "right": 1, "left_image": 1,
                                                 "text_h": "p", "text_l": {"class": "entry-content"},
                                                 "title_h": "h2", "title_l": {"class": "entry-content"}, "title_container": "div", "title_p": 1,
                                                 "link_h": "a", "link_l": {'text': '>>>'}},
                       "www.isotls.com":    {"left": 1, "right": 1, "left_image": 1,
                                            "text_h": "p", "text_l": {"class": "content"},
                                            "link_h": "a", "link_l": {'class': 'btn-group'}, "link_container": "div", "link_p": 2},
                       "www.royalroad.com": {"text_h": "p", "text_l": {"class": "chapter-content"}, "text_intelligent": True,
                                             "title_h": "h1",
                                             "link_h": "a", "link_l": {"class": "nav-buttons"}, "link_container": "div", "link_p": -1},
                       "exiledrebelsscanlations.com": {"text_h": "p", "text_l": {"id": "wtr-content"},
                                                       "link_h": "a", "link_l": {"class": "wp-post-navigation-next"},
                                                       "link_container": "div",
                                                       "title_h": "title", "left": 2},
                       "moonlightnovel.com": {"text_h": "p", "text_l": {"class": "epcontent"},
                                              "title_h": "empty",
                                              "link_h": "a", "link_l": {"rel": "next"}},
                       "www.novelcool.com": {"text_h": "p", "text_l": {"class": "chapter-reading-section"},
                                             "title_h": "h2", "title_l": {"class": "chapter-title"},
                                             "link_h": "a", "link_l": {"class": "chapter-reading-pagination"},
                                             "link_container": "div", "link_p": -1},
                       "dummynovels.com": {"text_h": "p", "text_l": {"class": "elementor-widget-theme-post-content"},
                                           "title_h": "h1", "title_l": {"class": "chapter-heading"},
                                           "link_h": "a", "link_l": {"class": "chapter-nav-next"}, "link_container": "div"},
                       "www.wuxiaworld.eu": {"text_h": "div", "text_l": {"id": "chapterText"},
                                             "title_h": "empty",
                                             "link_h": "a", "link_l": {"rel": "noreferrer"}, "link_p": -1},
                       "www.wuxiabee.com": {"text_h": "p", "text_l": {"class": "chapter-content"},
                                            "title_h": "h2",
                                            "link_h": "a", "link_l": {"class": "chapternav"}, "link_container": "div", "link_p": -1},
                       "www.asianovel.net": {"text_h": "div", "text_l": {"data-dir": "ltr"}, "text_container": "article",
                                             "title_h": "h2",
                                             "link_h": "a", "link_l": {"class": "pagination-single__right"}},
                       "wuxiaworld.ru": {"text_h": "p", "text_l": {"class": "js-full-content"}, "left": 1,
                                          "title_h": "empty",
                                          "link_h": "a", "link_l": {"rel": "Вперед"}},
                       "huahualibrary.wordpress.com": {"text_h": "p", "text_l": {"class": "entry-content"},
                                                       "title_h": "title", "left": 1,
                                                       "link_h": "a", "link_l": {"rel": "next"}},
                       "www.teanovel.com": {"text_h": "p", "text_l": {"class": "prose"},
                                             "title_h": "h1",
                                             "link_h": "a", "link_l": {"id": "buttons"}, "link_container": "div", "link_p": 2},
                       "novelhi.com": {"text_h": "sent", "text_l": {"id": "showReading"},
                                        "title_h": "h1", "title_l": {"class": "book_title"},
                                        "link_h": "a", "link_l": {"class": "next"}},
                       "novellive.net": {"text_h": "p", "text_l": {"class": "txt"},
                                         "title_h": "span", "title_l": {"class": "top"}, "title_container": "div",
                                         "link_h": "a", "link_l": {"id": "next"}},
                       "www.fansmtl.com": {"text_h": "p", "text_l": {"class": "chapter-content"},
                                           "title_h": "h2",
                                           "link_h": "a", "link_l": {"class": "chnav next"}},
                       "bambootriangle.wordpress.com": {"text_h": "p", "text_l": {"class": "entry-content"},
                                                        "title_h": "h1",
                                                        "link_h": "a", "link_l": {"class": "wp-block-buttons"}, "link_container": "div", "link_p": 2},
                       "whiteskytranslations.wordpress.com": {"text_h": "p", "text_l": {"class": "entry-content"}, "left": 2, "right": 1,
                                                              "title_h": "empty",
                                                              "link_h": "a", "link_l": {"class": "entry-content"}, "link_container": "div", "link_p": 2},
                       "novelbin.englishnovel.net": {"text_h": "p", "text_l": {"id": "chr-content"},
                                                     "title_h": "h4",
                                                     "link_h": "a", "link_l": {"id": "chr-nav-top"}, "link_container": "div", "link_p": -1},
                       "novelbjn.novelupdates.net": {"text_h": "p", "text_l": {"id": "chr-content"},
                                                    "title_h": "h2",
                                                    "link_h": "a", "link_l": {"id": "chr-nav-top"}, "link_container": "div", "link_p": -1,
                                                     "text_intelligent": True},
                       "neondragonfly.org": {"text_h": "p", "text_l": {"class": "entry-content"}, "right": 2,
                                             "title_h": "h1", "title_container": "main",
                                             "link_h": "a", "link_l": {"class": "nav-next"}, "link_container": "div"},
                       "www.lightnovelworld.co": {"text_h": "p", "text_l": {"class": "chapter-content"},
                                                  "title_h": "span", "title_l": {"class": "chapter-title"},
                                                  "link_h": "a", "link_l": {"rel": "next"}},
                       "lightnovel.novelcenter.net": {"text_h": "p", "text_l": {"id": "chr-content"}, "left": 2, "right": 18,
                                                     "title_h": "h3",
                                                     "link_h": "a", "link_l": {"id": "chr-nav-top"}, "link_container": "div", "link_p": -1},
                       "secondlifetranslations.com": {"text_h": "p", "text_l": {"class": "entry-content"},
                                                      "title_h": "h1",
                                                      "link_h": "a", "link_l": {"rel": "next"}, "text_intelligent": True, "text_lang": ['eng']},
                       "www.webnovelpub.pro": {"text_h": "p", "text_l": {"class": "chapter-content"},
                                               "title_h": "span", "title_l": {"class": "chapter-title"},
                                               "link_h": "a", "link_l": {"rel": "next"}},
                       "fast.novelupdates.net": {"text_h": "p", "text_l": {"id": "chr-content"},
                                                "title_h": "h3",
                                                "link_h": "a", "link_l": {"id": "chr-nav-top"}, "link_container": "div", "link_p": -1},
                       "ckandawrites.online": {"text_h": "p", "text_l": {"class": "entry-content"},
                                               "title_h": "h1",
                                               "link_h": "a", "link_l": {"rel": "next"}},
                       "knoxt.space": {"text_h": "p", "text_l": {"class": "entry-content"},
                                       "title_h": "h1",
                                       "link_h": "a", "link_l": {'rel': 'next'}},
                       "renovels.org": {"text_h": "p", "text_l": {"class": "content"},
                                       "title_h": "h1",
                                       "link_h": "button", "link_l": {"class": "items-center"}, "link_container": "div", "link_p": -1},
                       "novelbin.com": {"text_h": "p", "text_l": {"id": "chr-content"},
                                                     "title_h": "h4",
                                                     "link_h": "a", "link_l": {"id": "chr-nav-top"}, "link_container": "div", "link_p": -1},
                       "wuxia.click": {"text_h": "div", "text_l": {"id": "chapterText"}, "text_container": None,
                                             "title_h": "title",
                                             "link_h": "a", "link_l": {"rel": "noreferrer"}, "link_p": -1},
                       "shanghaifantasy.com": {"text_h": "p", "text_l": {"class": "contenta"},
                                                     "title_h": "title",
                                                     "link_h": "a", "link_l": {"rel": "next"}},
                       "novelbin.lanovels.net": {"text_h": "p", "text_l": {"id": "chr-content"},
                                                 "title_h": "h4",
                                                 "link_h": "a", "link_l": {"id": "chr-nav-top"}, "link_container": "div", "link_p": -1},
                       "m.novel-cat.com": {"text_h": "p", "text_l": {"class": "chapterContent"},
                                           "title_h": "h4",
                                           "link_h": "div", "link_l": {"class": "next_btn"}, "link_container": "div", "link_p": -1},
                       "www.goodnovel.com": {"text_h": "p", "text_l": {"class": "read-content"},
                                             "title_h": "h1",
                                             "link_h": "a", "link_l": {"class": "pagetion"}, "link_container": "div", "link_p": -1},
                       "tapas.io": {"text_h": "p", "text_container": "article",
                                    "title_h": "p", "title_l": {"class": "js-ep-title"},
                                    "link_h": "a", "link_l": {"class": "toolbar-btn--center","data-direction": "next"}, "press_link": True, "link_sleep_and_reload": True},
                       "silver-prince.com": {"text_h": "p", "text_container": "p", "text_l": {"class": "chapter"},
                                    "title_h": "h1",
                                    "link_h": "button", "link_container": "main", "link_p": 2, "link_pure_click": True},
                       "www.novelhall.com": {"text_l": {"id": "htmlContent"}, "tags_used": ['br'],
                                             "title_h": "h1",
                                             "link_h": "a", "link_l": {"rel": "next"}},
                       "ranobes.top": {"text_h": "p", "text_l": {"id": "arrticle"},
                                       "title_h": "h1",
                                       "link_h": "a", "link_l": {"id": "next"}},
                       "www.fanmtl.com": {"text_l": {"class": "chapter-content"}, "tags_used": ["br"],
                                       "title_h": "h2",
                                       "link_h": "a", "link_l": {"class": "chnav next"}},
                       "author.today": {"text_h": "p", "text_l": {"id": "text-container"},
                                       "title_h": "h1",
                                       "link_h": "a", "link_l": {"class": "next"}, "link_container": "li"},
                       "wtr-lab.com": {"text_h": "p", "text_l": {"class": "chapter-body"},
                                       "title_h": "h3",
                                       "link_h": "a", "link_l": {"class": "chapter-navigator"}, "link_container": "div", "link_p": -1, "press_link": False},
                       "sleepytranslations.com": {"text_h": "p", "text_l": {"class": "reading-content"},
                                                  "title_h": "h1",
                                                  "link_h": "a", "link_l": {"class": "nav-next"}, "link_container": "div"},
                       "www.silknovel.com": {"text_h": "p", "text_container": "article", "right": 2,
                                             "title_h": "h2",
                                             "link_h": "a", "link_l": {"class": "justify-end"}},
                       "loomywoods.com": {"text_h": "span", "text_l": {"class": "reading-content"},
                                          "title_h": "h1",
                                          "link_h": "a", "link_l": {"class": "next_page"}},
                       "littlepinkstarfish.com": {"text_h": "p", "text_l": {"class": "entry-content"},
                                          "title_h": "h2",
                                          "link_h": "a", "link_l": {"rel": "next"}},
                       "snowlyme.com": {"text_h": "p", "text_l": {"class": "entry-content"}, "right": 2,
                                          "title_h": "h2",
                                          "link_h": "a", "link_l": {"string": "Next"}},
                       "bittercoffeetranslations.com": {"text_h": ["p", "figure"], "text_l": {"class": "entry-content"}, "text_intelligent": True, "text_lang": ["eng"],
                                          "title_h": "h1",
                                          "link_h": "a", "link_l": {"class": "nav-next"}, "link_container": "div"},
                       "huitranslation.com": {"text_h": "p", "text_l": {"class": "reading-content"},
                                          "title_h": "h1",
                                          "link_h": "a", "link_l": {"class": "next_page"}}}
