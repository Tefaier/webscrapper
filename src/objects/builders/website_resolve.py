import re
from typing import Callable, Any

from dto.request import Request
from objects.elements.elements_finders import ByTextFinder, ByCssSelectorFinder
from objects.elements.elements_post_processings import ExcludeByCollectorFilter, SidesCutFiltering, JammedTextConverter
from objects.parsing_handlers.parsing_process import ParsingProcess
from objects.types.custom_exceptions import CommandException
from objects.types.driver_types import DriverTypes
from objects.types.order_stategy import OrderStrategy
from objects.web_handlers.block_screen_handler import ButtonClickHandler, CaptchaClickHandler
from objects.web_handlers.scroll_strategy import BottomScroll
from utils.extra_factory_functions import *


def resolve_website(website: str, request: Request) -> ParsingProcess:
    factory = ExtendedFactory(request.request_id)
    factory.output(request.file_extension)
    if website in chrome_websites:
        factory.selenium(chrome_websites[website])
    if website in scroll_websites.keys():
        factory.scroll(BottomScroll, **scroll_websites[website])
    if website in block_screen_websites:
        block_screen_websites[website](factory)
    if website in reload_websites:
        factory.reload_handler(**reload_websites[website])
    if website not in content_websites or website not in link_websites:
        raise CommandException(f"Unknown website - {website}")
    content_websites[website](factory)
    link_websites[website](factory)
    return factory.finish()


recognized_websites: List[str] = []
chrome_websites: Dict[str, DriverTypes] = {}
scroll_websites: Dict[str, Dict[str, Any]] = {}
block_screen_websites: Dict[str, Callable[[ExtendedFactory], Any]] = {}
reload_websites: Dict[str, Dict[str, Any]] = {}
content_websites: Dict[str, Callable[[ExtendedFactory], Any]] = {}
link_websites: Dict[str, Callable[[ExtendedFactory], Any]] = {}


def write_new_settings():
    # tl.rulate.ru
    website = "tl.rulate.ru"
    recognized_websites.append(website)
    block_screen_websites[website] = lambda factory: (
        factory.finder(
            f"{FINDER_NAME}_block_0", ByAttributesFinder, search_types=["button"], search_limits={"name": "ok"}
        ),
        factory.main_block_handler(ButtonClickHandler, button_finder=f"${FINDER_NAME}_block_0"),
    )

    # gravitytales.com
    website = "gravitytales.com"
    recognized_websites.append(website)
    content_websites[website] = lambda factory: (
        simple_title(factory, ["h1"]),
        simple_text(factory, ["section"], {"id": "chapter-content"}),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: simple_link(
        factory, ["div"], {"class": "chapter__actions-right"}, ["a"], {}, -1
    )

    # www.novelhall.com
    website = "www.novelhall.com"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.Undetected
    content_websites[website] = lambda factory: (
        simple_title(factory, ["h1"]),
        split_text(factory, ["div"], {"class": "entry-content"}, ["br"]),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: simple_link(factory, link_type=["a"], link_limit={"rel": "next"})

    # ru.novelcool.com
    website = "ru.novelcool.com"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.Undetected
    content_websites[website] = lambda factory: (
        simple_title(factory, ["h2"]),
        factory.finder(
            f"{FINDER_NAME}_exclude_0",
            ByAttributesFinder,
            search_types=["p"],
            search_limits={"class": "chapter-end-mark"},
        ).post_processing(
            f"{POST_PROCESSING_NAME}_text_0", ExcludeByCollectorFilter, finder=f"${FINDER_NAME}_exclude_0"
        ),
        simple_text(
            factory,
            ["div"],
            {"class": "chapter-reading-section"},
            ["p"],
            extra_post_processors=[f"{POST_PROCESSING_NAME}_text_0"],
        ),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: (
        factory.finder(
            f"{FINDER_NAME}_link_0",
            ByAttributesFinder,
            search_types=["div"],
            search_limits={"class": "chapter-reading-pagination"},
        )
        .finder(f"{FINDER_NAME}_link_1", ByTextFinder, search_types=["a"], inner_context="Далее > >")
        .link_collector([f"{FINDER_NAME}_link_0", f"{FINDER_NAME}_link_1"])
    )

    # www.novelcool.com
    website = "www.novelcool.com"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.Undetected
    content_websites[website] = content_websites["ru.novelcool.com"]
    link_websites[website] = lambda factory: (
        factory.finder(
            f"{FINDER_NAME}_link_0",
            ByAttributesFinder,
            search_types=["div"],
            search_limits={"class": "chapter-reading-pagination"},
        )
        .finder(f"{FINDER_NAME}_link_1", ByTextFinder, search_types=["a"], inner_context="Next>>")
        .link_collector([f"{FINDER_NAME}_link_0", f"{FINDER_NAME}_link_1"])
    )

    # betwixtedbutterfly.com
    website = "betwixtedbutterfly.com"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.Undetected
    content_websites[website] = lambda factory: (
        simple_title(factory, ["h1"], {"class": "post-title"}),
        simple_text(factory, ["div"], {"data-elementor-type": "wp-post"}, ["p"]),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: (
        factory.finder(
            f"{FINDER_NAME}_link_0",
            ByAttributesFinder,
            search_types=["div"],
            search_limits={"data-elementor-type": "wp-post"},
        )
        .finder(
            f"{FINDER_NAME}_link_1",
            ByAttributesFinder,
            search_types=["section"],
            search_limits={"class": "elementor-inner-section"},
        )
        .finder(f"{FINDER_NAME}_link_2", ByAttributesFinder, search_types=["a"])
        .post_processing(f"{POST_PROCESSING_NAME}_link_0", ExactElementTaker, take_at_index=-1)
        .link_collector(
            [f"{FINDER_NAME}_link_0", f"{FINDER_NAME}_link_1", f"{FINDER_NAME}_link_2"],
            [f"{POST_PROCESSING_NAME}_link_0"],
        )
    )

    # ranobelib.me
    website = "ranobelib.me"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.Regular
    content_websites[website] = lambda factory: (
        simple_title(factory, ["h1"]),
        simple_text(factory, ["div"], {"class": "text-content"}),
        factory.finder(f"{FINDER_NAME}_image_0", ByAttributesFinder, search_types=["img"]),
        factory.collector(
            f"{COLLECTOR_NAME}_image", FieldTypes.Image, [f"{FINDER_NAME}_text_0", f"{FINDER_NAME}_image_0"]
        ),
        factory.orderer(OrderStrategy.BY_SOURCELINE),
        orchestra(factory, with_images=True),
    )
    link_websites[website] = lambda factory: (
        factory.finder(f"{FINDER_NAME}_link_0", ByAttributesFinder, search_types=["header"])
        .finder(f"{FINDER_NAME}_link_1", ByCssSelectorFinder, selector="div > div:nth-child(3) > div + a")
        .link_collector([f"{FINDER_NAME}_link_0", f"{FINDER_NAME}_link_1"])
    )
    reload_websites[website] = {"sleep_before_process": True, "sleep_before_process_seconds": 5}

    # novelbin.com
    website = "novelbin.com"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.Undetected
    content_websites[website] = lambda factory: (
        simple_title(factory, ["h2"]),
        simple_text(factory, ["div"], {"id": "chr-content"}, ["p"]),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: simple_link(factory, link_type=["a"], link_limit={"id": "next_chap"})

    # ficbook.net
    website = "ficbook.net"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.Undetected
    content_websites[website] = lambda factory: (
        factory.finder(f"{FINDER_NAME}_title_0", ByAttributesFinder, search_types=["h2"])
        .post_processing(f"{POST_PROCESSING_NAME}_title_0", ExactElementTaker, take_at_index=0)
        .collector(
            f"{COLLECTOR_NAME}_title",
            FieldTypes.Text,
            [f"{FINDER_NAME}_title_0"],
            [f"{POST_PROCESSING_NAME}_title_0"] + DEFAULT_POST_PROCESSINGS,
        ),
        split_text(factory, ["div"], {"id": "content"}, ["div"]),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: simple_link(factory, link_type=["a"], link_limit={"class": "btn-next"})

    # 98novels.com
    website = "98novels.com"
    recognized_websites.append(website)
    content_websites[website] = lambda factory: (
        simple_title(factory, ["h1"]),
        factory.finder(
            f"{FINDER_NAME}_exclude_0",
            ByAttributesFinder,
            search_types=["p"],
            search_limits={"class": "has-text-align-center"},
        ),
        factory.post_processing(
            f"{POST_PROCESSING_NAME}_exclude_0", ExcludeByCollectorFilter, finder=f"${FINDER_NAME}_exclude_0"
        ),
        factory.post_processing(f"{POST_PROCESSING_NAME}_cut_0", SidesCutFiltering, cut_from_ending=1),
        factory.post_processing(f"{POST_PROCESSING_NAME}_split_0", SplitTagContentByInnerTags, split_tag_names=["br"]),
        simple_text(
            factory,
            ["div"],
            {"class": "kenta-article-content"},
            ["p"],
            extra_post_processors=[
                f"{POST_PROCESSING_NAME}_exclude_0",
                f"{POST_PROCESSING_NAME}_cut_0",
                f"{POST_PROCESSING_NAME}_split_0",
            ],
        ),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: simple_link(
        factory, holder_type=["div"], holder_limit={"class": "nav-buttons"}, link_type=["a"], link_exact=-1
    )

    # chrysanthemumgarden.com
    website = "chrysanthemumgarden.com"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.Undetected
    content_websites[website] = lambda factory: (
        simple_title(factory, ["title"]),
        factory.finder(
            f"{FINDER_NAME}_jam_0",
            ByAttributesFinder,
            search_types=["span"],
            search_limits={"style": re.compile("font-family: \w+;")},
        ),
        factory.post_processing(
            f"{POST_PROCESSING_NAME}_jam_0",
            JammedTextConverter,
            jammed_finder=f"${FINDER_NAME}_jam_0",
            expected_languages="eng",
        ),
        simple_text(
            factory,
            ["div"],
            {"id": "novel-content"},
            ["p"],
            extra_post_processors=[
                f"{POST_PROCESSING_NAME}_jam_0",
            ],
        ),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: simple_link(factory, link_type=["a"], link_limit={"class": "nav-next"})

    # novelight.net
    website = "novelight.net"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.CDP
    content_websites[website] = lambda factory: (
        simple_title(factory, ["title"]),
        factory.finder(
            f"{FINDER_NAME}_text_0",
            ByAttributesFinder,
            search_types=["div"],
            search_limits={"class": "chapter-text"},
        ),
        factory.finder(f"{FINDER_NAME}_text_1", ByCssSelectorFinder, selector='div:not([class*="advertisment"])'),
        factory.collector(
            f"{COLLECTOR_NAME}_text",
            FieldTypes.Text,
            [f"{FINDER_NAME}_text_0", f"{FINDER_NAME}_text_1"],
            DEFAULT_POST_PROCESSINGS,
        ),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: (
        factory.link_handler(press_link=False),
        simple_link(factory, holder_type=["div"], holder_limit={"class": "pagination"}, link_type=["a"], link_exact=-1),
    )

    # novellive.app
    website = "novellive.app"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.CDP
    content_websites[website] = lambda factory: (
        simple_title(factory, ["span"], {"class": "chapter"}),
        remover := by_content_remove(
            factory,
            "royal_road",
            ["p, li"],
            re.compile(rf'\b(?:{re.escape("Amazon")}|{re.escape("Royal road")})\b', re.IGNORECASE),
        ),
        simple_text(factory, holder_limit={"class": "txt"}, text_type=["p", "li"], extra_post_processors=[remover]),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: (
        simple_link(
            factory,
            holder_type=["div"],
            holder_limit={"class": "top"},
            link_type=["a"],
            link_limit={"title": "Read Next Chapter"},
        ),
    )

    # www.asianovel.net
    website = "www.asianovel.net"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.Undetected
    content_websites[website] = lambda factory: (
        simple_title(factory, ["h1"]),
        simple_text(
            factory,
            holder_type=["section"],
            holder_limit={"id": "chapter-content"},
            text_type=["p"],
            text_limit={"id": re.compile("paragraph-\d+")},
        ),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: (
        simple_link(
            factory,
            link_type=["a"],
            link_limit={"class": "_next"},
        ),
    )

    # novelhi.com
    website = "novelhi.com"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.Undetected
    content_websites[website] = lambda factory: (
        simple_title(factory, ["h1"]),
        simple_text(
            factory,
            holder_type=["div"],
            holder_limit={"id": "showReading"},
            text_type=["sent"],
        ),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: (
        simple_link(
            factory,
            link_type=["a"],
            link_limit={"class": "next"},
        ),
    )

    # dummynovels.com
    website = "dummynovels.com"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.CDP
    content_websites[website] = lambda factory: (
        simple_title(factory, ["h1"], {"class": "chapter-heading"}),
        simple_text(factory, ["div"], {"class": "elementor-widget-theme-post-content"}, ["p", "div"]),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: (simple_link(factory, ["div"], {"class": "chapter-nav-next"}, ["a"]))

    # starcafe.me
    website = "starcafe.me"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.Undetected
    content_websites[website] = lambda factory: (
        factory.post_processing(f"{POST_PROCESSING_NAME}_title_0", ExactElementTaker, take_at_index=0),
        factory.post_processing(f"{POST_PROCESSING_NAME}_title_1", ExactElementTaker, take_at_index=-1),
        factory.finder(f"{FINDER_NAME}_title_0", ByAttributesFinder, search_types=["h2"]),
        factory.finder(f"{FINDER_NAME}_title_1", ByAttributesFinder, search_types=["h3"]),
        factory.collector(
            f"{COLLECTOR_NAME}_title_0",
            FieldTypes.Text,
            [f"{FINDER_NAME}_title_0"],
            [f"{POST_PROCESSING_NAME}_title_0"] + DEFAULT_POST_PROCESSINGS,
        ),
        factory.collector(
            f"{COLLECTOR_NAME}_title_1",
            FieldTypes.Text,
            [f"{FINDER_NAME}_title_1"],
            [f"{POST_PROCESSING_NAME}_title_1"] + DEFAULT_POST_PROCESSINGS,
        ),
        simple_text(factory, ["div"], {"class": "no-select"}, ["p"]),
        factory.orchestra([f"{COLLECTOR_NAME}_title_0", f"{COLLECTOR_NAME}_title_1", f"{COLLECTOR_NAME}_text"]),
    )
    link_websites[website] = lambda factory: (
        simple_link(factory, link_type=["button"], link_limit={"title": "Next Chapter"})
    )

    # littlepinkstarfish.com
    website = "littlepinkstarfish.com"
    recognized_websites.append(website)
    content_websites[website] = lambda factory: (
        simple_title(factory, ["h2"], {"class", "wp-block-post-title"}),
        factory.post_processing(f"{POST_PROCESSING_NAME}_cut_0", SidesCutFiltering, cut_from_ending=4),
        factory.post_processing(f"{POST_PROCESSING_NAME}_split_0", SplitTagContentByInnerTags, split_tag_names=["br"]),
        simple_text(
            factory,
            ["div"],
            {"class": "entry-content"},
            ["p", "h3", "li"],
            extra_post_processors=[f"{POST_PROCESSING_NAME}_cut_0", f"{POST_PROCESSING_NAME}_split_0"],
        ),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: (simple_link(factory, link_type=["a"], link_limit={"rel": "next"}))

    # littlepinkstarfish.wordpress.com
    website = "littlepinkstarfish.wordpress.com"
    recognized_websites.append(website)
    content_websites[website] = content_websites["littlepinkstarfish.com"]
    link_websites[website] = link_websites["littlepinkstarfish.com"]

    # www.royalroad.com
    website = "www.royalroad.com"
    recognized_websites.append(website)
    content_websites[website] = lambda factory: (
        simple_text(factory, ["h1"]),
        simple_text(factory, ["div"], {"class": "chapter-content"}, ["p"]),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: (
        factory.finder(
            f"{FINDER_NAME}_link_0",
            ByCssSelectorFinder,
            selector="div.nav-buttons > div:nth-of-type(2) > a:first-of-type",
        ),
        factory.link_collector([f"{FINDER_NAME}_link_0"], []),
    )

    # 18.foxaholic.com
    website = "18.foxaholic.com"
    recognized_websites.append(website)
    chrome_websites[website] = DriverTypes.CDP
    content_websites[website] = lambda factory: (
        factory.main_block_handler(CaptchaClickHandler),
        simple_title(factory, ["title"]),
        simple_text(factory, holder_type=["div"], holder_limit={"class": "text-left"}, text_type=["p"]),
        orchestra(factory),
    )
    link_websites[website] = lambda factory: (simple_link(factory, link_type=["a"], link_limit={"class": "next_page"}))


write_new_settings()

# FROM HERE BACKWARD COMPATIBILITY LIMITED SUPPORT

active_process_dicts = {
    "ranobehub.org": {"chrome": False},
    "jaomix.ru": {"chrome": False},
    "ranobes.com": {"chrome": True},
    "ranobes.net": {"chrome": True, "sleep": True},
    "tl.rulate.ru": {
        "chrome": True,
        "min_len": 2000,
        "block_screen": True,
        "button_type": "",
        "button_limit": {"name": "ok"},
    },
    "www.wattpad.com": {"chrome": True, "scroll": True, "min_par": 1, "wait": True},
    "www.readlightnovel.me": {"chrome": False},
    "www.mtlnovel.com": {"chrome": True, "clearing": True, "sleep": True},
    "www.mtlnovels.com": {},  # {"chrome": True, "clearing": True, "chrome_undetected": True},
    "www.foxaholic.com": {
        "chrome": True,
        "wait": True,
    },
    "rainbow-reads.com": {"chrome": False},
    "danmeiextra.home.blog": {"chrome": False},
    "younettranslate.com": {"chrome": False},
    "strictlybromance.com": {"chrome": True},
    "kinkytranslations.com": {"chrome": False},
    "www.isotls.com": {"chrome": False},
    "exiledrebelsscanlations.com": {"chrome": False},
    "moonlightnovel.com": {"chrome": False},
    "www.wuxiaworld.eu": {"chrome": False},
    "www.wuxiabee.com": {"chrome": True},
    "wuxiaworld.ru": {"chrome": False},
    "huahualibrary.wordpress.com": {},
    "www.teanovel.com": {},
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
    "wuxia.click": {"chrome": True, "sleep": True},
    "shanghaifantasy.com": {"chrome": True, "wait": True},
    "novelbin.lanovels.net": {"chrome": True},
    "m.novel-cat.com": {"chrome": True, "wait": True},
    "www.goodnovel.com": {},
    "tapas.io": {"chrome": True, "wait": True},
    "silver-prince.com": {"chrome": True, "wait": True},
    "ranobes.top": {"chrome": True, "chrome_undetected": True},
    "www.fanmtl.com": {"chrome": True},
    "author.today": {"chrome": True, "wait": True},
    "wtr-lab.com": {"chrome": True},
    "sleepytranslations.com": {"chrome": True},
    "www.silknovel.com": {},
    "loomywoods.com": {"chrome": True},
    "snowlyme.com": {"chrome": True},
    "bittercoffeetranslations.com": {"chrome": True, "wait": True},
    "huitranslation.com": {},
    "ididmybesttranslations.wordpress.com": {},
    "kktranslates.home.blog": {"chrome": True, "wait": True},
}

active_parser_dicts = {
    "ranobehub.org": {
        "left": 0,
        "right": 4,
        "text_h": "p",
        "text_container": None,
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"data-hotkey": "right"},
    },
    "jaomix.ru": {
        "left": 2,
        "right": 3,
        "text_h": "p",
        "text_l": None,
        "title_h": "h1",
        "title_l": None,
        "link_h": "a",
        "link_l": {"class": "next"},
        "link_p": 0,
        "link_container": "li",
    },
    "ranobes.com": {
        "text_h": ["p", "blockquote"],
        "text_l": {"id": "arrticle"},
        # "tags_used": ["br", "div"]
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"id": "next"},
    },
    "ranobes.net": {
        "left": 0,
        "right": 0,
        "text_h": "p",
        "text_l": None,
        "title_h": "title",
        "title_l": None,
        "link_h": "a",
        "link_l": {"id": "next"},
    },
    "tl.rulate.ru": {
        "left": 0,
        "right": 1,
        "text_h": "p",
        "text_l": {"class": "content-text"},
        "title_h": "title",
        "link_h": "a",
        "link_l": {"class": "next"},
        "link_p": 0,
        "link_container": "li",
    },
    "www.wattpad.com": {
        "left": 0,
        "right": 0,
        "text_h": "p",
        "text_l": {"class", "part-content"},
        "text_container": "div",
        "title_h": "h1",
        "title_l": {"class", "h2"},
        "link_h": "a",
        "link_l": {"id": "story-part-navigation"},
        "link_container": "div",
    },
    "www.readlightnovel.me": {
        "left": 1,
        "right": 0,
        "text_h": "p",
        "text_l": {"class": "desc"},
        "title_h": "title",
        "title_l": None,
        "link_h": "a",
        "link_l": {"class": "next next-link"},
    },
    "www.mtlnovel.com": {
        "left": 0,
        "right": 0,
        "text_h": "p",
        "text_l": None,
        "title_h": "h1",
        "title_l": None,
        "link_h": "a",
        "link_l": {"class": "next"},
    },
    "www.mtlnovels.com": {
        "left": 0,
        "right": 0,
        "text_h": "p",
        "text_l": {"class", "par"},
        "title_h": "h1",
        "title_l": None,
        "link_h": "a",
        "link_l": {"class": "next"},
    },
    "www.foxaholic.com": {
        "left": 0,
        "right": 0,
        "text_h": "p",
        "text_l": {"class": "entry-content"},
        "title_h": "title",
        "title_l": None,
        "link_h": "a",
        "link_l": {"class": "next_page"},
    },
    "rainbow-reads.com": {
        "left": 0,
        "right": 1,
        "text_h": "p",
        "text_l": {"class": "post-content"},
        "title_h": "h1",
        "title_l": None,
        "link_h": "a",
        "link_l": {"text": "Next Page »"},
    },
    "danmeiextra.home.blog": {
        "left": 1,
        "right": 2,
        "text_h": "p",
        "text_l": {"class": "entry-content"},
        "title_h": "empty",
        "title_l": None,
        "link_h": "a",
        "link_l": {"text": "Next Chapter"},
    },
    "younettranslate.com": {
        "left": 0,
        "right": 0,
        "text_h": "p",
        "text_l": {"class": "postdata-content"},
        "title_h": "title",
        "title_l": None,
        "link_h": "a",
        "link_l": {"class": "chapters-navpanel"},
        "link_by_div": True,
        "link_p": -1,
    },
    "strictlybromance.com": {
        "left": 1,
        "right": 1,
        "text_h": "p",
        "text_l": {"class": "post-content"},
        "title_h": "title",
        "title_l": None,
        "link_h": "a",
        "link_l": {"class": "wp-next-post-navi-next"},
        "link_by_div": True,
    },
    "kinkytranslations.com": {
        "left": 1,
        "right": 1,
        "left_image": 1,
        "text_h": "p",
        "text_l": {"class": "entry-content"},
        "title_h": "h2",
        "title_l": {"class": "entry-content"},
        "title_container": "div",
        "title_p": 1,
        "link_h": "a",
        "link_l": {"text": ">>>"},
    },
    "www.isotls.com": {
        "left": 1,
        "right": 1,
        "left_image": 1,
        "text_h": "p",
        "text_l": {"class": "content"},
        "link_h": "a",
        "link_l": {"class": "btn-group"},
        "link_container": "div",
        "link_p": 2,
    },
    "exiledrebelsscanlations.com": {
        "text_h": "p",
        "text_l": {"id": "wtr-content"},
        "link_h": "a",
        "link_l": {"class": "wp-post-navigation-next"},
        "link_container": "div",
        "title_h": "title",
        "left": 2,
    },
    "moonlightnovel.com": {
        "text_h": "p",
        "text_l": {"class": "epcontent"},
        "title_h": "empty",
        "link_h": "a",
        "link_l": {"rel": "next"},
    },
    "www.wuxiaworld.eu": {
        "text_h": "div",
        "text_l": {"id": "chapterText"},
        "title_h": "empty",
        "link_h": "a",
        "link_l": {"rel": "noreferrer"},
        "link_p": -1,
    },
    "www.wuxiabee.com": {
        "text_h": "p",
        "text_l": {"class": "chapter-content"},
        "title_h": "h2",
        "link_h": "a",
        "link_l": {"class": "chapternav"},
        "link_container": "div",
        "link_p": -1,
    },
    "wuxiaworld.ru": {
        "text_h": "p",
        "text_l": {"class": "js-full-content"},
        "left": 1,
        "title_h": "empty",
        "link_h": "a",
        "link_l": {"rel": "Вперед"},
    },
    "huahualibrary.wordpress.com": {
        "text_h": "p",
        "text_l": {"class": "entry-content"},
        "title_h": "title",
        "left": 1,
        "link_h": "a",
        "link_l": {"rel": "next"},
    },
    "www.teanovel.com": {
        "text_h": "p",
        "text_l": {"class": "prose"},
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"id": "buttons"},
        "link_container": "div",
        "link_p": 2,
    },
    "novellive.net": {
        "text_h": "p",
        "text_l": {"class": "txt"},
        "title_h": "span",
        "title_l": {"class": "top"},
        "title_container": "div",
        "link_h": "a",
        "link_l": {"id": "next"},
    },
    "www.fansmtl.com": {
        "text_h": "p",
        "text_l": {"class": "chapter-content"},
        "title_h": "h2",
        "link_h": "a",
        "link_l": {"class": "chnav next"},
    },
    "bambootriangle.wordpress.com": {
        "text_h": "p",
        "text_l": {"class": "entry-content"},
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"class": "wp-block-buttons"},
        "link_container": "div",
        "link_p": 2,
    },
    "whiteskytranslations.wordpress.com": {
        "text_h": "p",
        "text_l": {"class": "entry-content"},
        "left": 2,
        "right": 1,
        "title_h": "empty",
        "link_h": "a",
        "link_l": {"class": "entry-content"},
        "link_container": "div",
        "link_p": 2,
    },
    "novelbin.englishnovel.net": {
        "text_h": "p",
        "text_l": {"id": "chr-content"},
        "title_h": "h4",
        "link_h": "a",
        "link_l": {"id": "chr-nav-top"},
        "link_container": "div",
        "link_p": -1,
    },
    "novelbjn.novelupdates.net": {
        "text_h": "p",
        "text_l": {"id": "chr-content"},
        "title_h": "h2",
        "link_h": "a",
        "link_l": {"id": "chr-nav-top"},
        "link_container": "div",
        "link_p": -1,
        "text_intelligent": True,
    },
    "neondragonfly.org": {
        "text_h": "p",
        "text_l": {"class": "entry-content"},
        "right": 2,
        "title_h": "h1",
        "title_container": "main",
        "link_h": "a",
        "link_l": {"class": "nav-next"},
        "link_container": "div",
    },
    "www.lightnovelworld.co": {
        "text_h": "p",
        "text_l": {"class": "chapter-content"},
        "title_h": "span",
        "title_l": {"class": "chapter-title"},
        "link_h": "a",
        "link_l": {"rel": "next"},
    },
    "lightnovel.novelcenter.net": {
        "text_h": "p",
        "text_l": {"id": "chr-content"},
        "left": 2,
        "right": 18,
        "title_h": "h3",
        "link_h": "a",
        "link_l": {"id": "chr-nav-top"},
        "link_container": "div",
        "link_p": -1,
    },
    "secondlifetranslations.com": {
        "text_h": "p",
        "text_l": {"class": "entry-content"},
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"rel": "next"},
        "text_intelligent": True,
        "text_lang": ["eng"],
    },
    "www.webnovelpub.pro": {
        "text_h": "p",
        "text_l": {"class": "chapter-content"},
        "title_h": "span",
        "title_l": {"class": "chapter-title"},
        "link_h": "a",
        "link_l": {"rel": "next"},
    },
    "fast.novelupdates.net": {
        "text_h": "p",
        "text_l": {"id": "chr-content"},
        "title_h": "h3",
        "link_h": "a",
        "link_l": {"id": "chr-nav-top"},
        "link_container": "div",
        "link_p": -1,
    },
    "ckandawrites.online": {
        "text_h": "p",
        "text_l": {"class": "entry-content"},
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"rel": "next"},
    },
    "knoxt.space": {
        "text_h": "p",
        "text_l": {"class": "entry-content"},
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"rel": "next"},
    },
    "renovels.org": {
        "text_h": "p",
        "text_l": {"class": "content"},
        "title_h": "h1",
        "link_h": "button",
        "link_l": {"class": "items-center"},
        "link_container": "div",
        "link_p": -1,
    },
    "wuxia.click": {
        "text_h": "div",
        "text_l": {"id": "chapterText"},
        "text_container": None,
        "title_h": "title",
        "link_h": "a",
        "link_l": {"rel": "noreferrer"},
        "link_p": -1,
    },
    "shanghaifantasy.com": {
        "text_h": "p",
        "text_l": {"class": "contenta"},
        "title_h": "title",
        "link_h": "a",
        "link_l": {"rel": "next"},
    },
    "novelbin.lanovels.net": {
        "text_h": "p",
        "text_l": {"id": "chr-content"},
        "title_h": "h4",
        "link_h": "a",
        "link_l": {"id": "chr-nav-top"},
        "link_container": "div",
        "link_p": -1,
    },
    "m.novel-cat.com": {
        "text_h": "p",
        "text_l": {"class": "chapterContent"},
        "title_h": "h4",
        "link_h": "div",
        "link_l": {"class": "next_btn"},
        "link_container": "div",
        "link_p": -1,
    },
    "www.goodnovel.com": {
        "text_h": "p",
        "text_l": {"class": "read-content"},
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"class": "pagetion"},
        "link_container": "div",
        "link_p": -1,
    },
    "tapas.io": {
        "text_h": "p",
        "text_container": "article",
        "title_h": "p",
        "title_l": {"class": "js-ep-title"},
        "link_h": "a",
        "link_l": {"class": "toolbar-btn--center", "data-direction": "next"},
        "press_link": True,
        "link_sleep_and_reload": True,
    },
    "silver-prince.com": {
        "text_h": "p",
        "text_container": "p",
        "text_l": {"class": "chapter"},
        "title_h": "h1",
        "link_h": "button",
        "link_container": "main",
        "link_p": 2,
        "link_pure_click": True,
    },
    "ranobes.top": {
        "text_h": "p",
        "text_l": {"id": "arrticle"},
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"id": "next"},
    },
    "www.fanmtl.com": {
        "text_l": {"class": "chapter-content"},
        "tags_used": ["br"],
        "title_h": "h2",
        "link_h": "a",
        "link_l": {"class": "chnav next"},
    },
    "author.today": {
        "text_h": "p",
        "text_l": {"id": "text-container"},
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"class": "next"},
        "link_container": "li",
    },
    "wtr-lab.com": {
        "text_h": "p",
        "text_l": {"class": "chapter-body"},
        "title_h": "h3",
        "link_h": "a",
        "link_l": {"class": "chapter-navigator"},
        "link_container": "div",
        "link_p": -1,
        "press_link": False,
    },
    "sleepytranslations.com": {
        "text_h": "p",
        "text_l": {"class": "reading-content"},
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"class": "nav-next"},
        "link_container": "div",
    },
    "www.silknovel.com": {
        "text_h": "p",
        "text_container": "article",
        "right": 2,
        "title_h": "h2",
        "link_h": "a",
        "link_l": {"class": "justify-end"},
    },
    "loomywoods.com": {
        "text_h": "span",
        "text_l": {"class": "reading-content"},
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"class": "next_page"},
    },
    "snowlyme.com": {
        "text_h": "p",
        "text_l": {"class": "entry-content"},
        "right": 2,
        "title_h": "h2",
        "link_h": "a",
        "link_l": {"string": "Next"},
    },
    "bittercoffeetranslations.com": {
        "text_h": ["p", "figure"],
        "text_l": {"class": "entry-content"},
        "text_intelligent": True,
        "text_lang": ["eng"],
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"class": "nav-next"},
        "link_container": "div",
    },
    "huitranslation.com": {
        "text_h": "p",
        "text_l": {"class": "reading-content"},
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"class": "next_page"},
    },
    "ididmybesttranslations.wordpress.com": {
        "text_h": "p",
        "text_l": {"class": "entry-content"},
        "title_h": "header",
        "title_l": {"class": "entry-header"},
        "link_h": "a",
        "link_l": {"text": "Next Chapter"},
    },
    "kktranslates.home.blog": {
        "text_h": "p",
        "text_l": {"class": "entry-content"},
        "title_h": "h2",
        "link_h": "a",
        "link_container": "p",
        "link_l": {"class": "has-text-align-center"},
        "link_p": -1,
    },
}

# === Auto-conversion from old settings to new structure ===
# Populate chrome/undetected/scroll/reload from active_process_dicts
for _site, _pcfg in active_process_dicts.items():
    if _pcfg.get("chrome"):
        if _site not in chrome_websites:
            chrome_websites[_site] = DriverTypes.Regular
    if _pcfg.get("chrome_undetected"):
        chrome_websites[_site] = DriverTypes.Undetected
    if _pcfg.get("scroll"):
        scroll_websites.setdefault(_site, {})
    if _pcfg.get("wait") or _pcfg.get("sleep"):
        _reload = reload_websites.setdefault(_site, {})
        if _pcfg.get("wait"):
            _reload["wait_before_open"] = True
        if _pcfg.get("sleep"):
            _reload["sleep_before_open"] = True

# Helpers for building content/link website configs from parser dicts
from typing import Union


def _to_list(v: Union[str, List[str], None]) -> List[str]:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def _mk_content(site_cfg: Dict[str, Any]) -> Callable[[ExtendedFactory], Any]:
    def _content(factory: ExtendedFactory) -> ExtendedFactory:
        # Title setup
        title_h = site_cfg.get("title_h", "title")
        title_l = site_cfg.get("title_l")
        title_container = site_cfg.get("title_container")
        if title_container:
            factory.finder(f"{FINDER_NAME}_title_0", ByAttributesFinder, search_types=_to_list(title_container))
            factory.finder(
                f"{FINDER_NAME}_title_1",
                ByAttributesFinder,
                search_types=_to_list(title_h if title_h != "empty" else "title"),
                search_limits=title_l,
            )
            factory.collector(
                f"{COLLECTOR_NAME}_title",
                FieldTypes.Text,
                [f"{FINDER_NAME}_title_0", f"{FINDER_NAME}_title_1"],
            )
        else:
            factory.finder(
                f"{FINDER_NAME}_title_0",
                ByAttributesFinder,
                search_types=_to_list(title_h if title_h != "empty" else "title"),
                search_limits=title_l,
            )
            factory.collector(
                f"{COLLECTOR_NAME}_title",
                FieldTypes.Text,
                [f"{FINDER_NAME}_title_0"],
            )

        # Text/content setup
        text_h = site_cfg.get("text_h", "p")
        text_l = site_cfg.get("text_l")
        text_container = site_cfg.get("text_container", "div")
        factory.finder(
            f"{FINDER_NAME}_text_0", ByAttributesFinder, search_types=_to_list(text_container), search_limits=text_l
        )
        factory.finder(f"{FINDER_NAME}_text_1", ByAttributesFinder, search_types=_to_list(text_h))
        factory.collector(
            f"{COLLECTOR_NAME}_text",
            FieldTypes.Text,
            [f"{FINDER_NAME}_text_0", f"{FINDER_NAME}_text_1"],
            DEFAULT_POST_PROCESSINGS,
        )

        # Orchestrate title + text collectors
        factory.orchestra([f"{COLLECTOR_NAME}_title", f"{COLLECTOR_NAME}_text"])
        return factory

    return _content


def _mk_link(site_cfg: Dict[str, Any]) -> Callable[[ExtendedFactory], Any]:
    def _link(factory: ExtendedFactory) -> ExtendedFactory:
        link_h = site_cfg.get("link_h", "a")
        link_l = site_cfg.get("link_l")
        link_container = site_cfg.get("link_container")
        pointer = site_cfg.get("link_p")
        if link_container:
            factory.finder(
                f"{FINDER_NAME}_link_0", ByAttributesFinder, search_types=_to_list(link_container), search_limits=link_l
            )
            factory.finder(f"{FINDER_NAME}_link_1", ByAttributesFinder, search_types=_to_list(link_h))
            if pointer:
                factory.post_processing(f"{POST_PROCESSING_NAME}_link_0", ExactElementTaker, take_at_index=-1)
                factory.link_collector(
                    [f"{FINDER_NAME}_link_0", f"{FINDER_NAME}_link_1"], [f"{POST_PROCESSING_NAME}_link_0"]
                )
            else:
                factory.link_collector([f"{FINDER_NAME}_link_0", f"{FINDER_NAME}_link_1"])
        else:
            factory.finder(
                f"{FINDER_NAME}_link_0", ByAttributesFinder, search_types=_to_list(link_h), search_limits=link_l
            )
            factory.link_collector([f"{FINDER_NAME}_link_0"])
            if pointer:
                factory.post_processing(f"{POST_PROCESSING_NAME}_link_0", ExactElementTaker, take_at_index=-1)
                factory.link_collector([f"{FINDER_NAME}_link_0"], [f"{POST_PROCESSING_NAME}_link_0"])
            else:
                factory.link_collector([f"{FINDER_NAME}_link_0"])
        return factory

    return _link


# Build content/link entries for every website declared in old parser dict
for _site, _cfg in active_parser_dicts.items():
    recognized_websites.append(_site)
    content_websites[_site] = _mk_content(_cfg)
    link_websites[_site] = _mk_link(_cfg)
