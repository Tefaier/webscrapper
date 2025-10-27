from typing import Dict, Callable, Any, List, Optional

from objects.builders.extended_factory import ExtendedFactory
from objects.elements.elements_finders import ByAttributesFinder
from objects.elements.elements_post_processings import ExactElementTaker
from objects.parsing_handlers.parsing_process import ParsingProcess
from objects.types.custom_exceptions import CommandException
from objects.types.field_types import FieldTypes
from objects.web_handlers.block_screen_handler import ButtonClickHandler
from objects.web_handlers.scroll_strategy import BottomScroll
from settings.builders_defaults import *


def resolve_website(website: str, request_id: str) -> ParsingProcess:
    factory = ExtendedFactory(request_id)
    if website in chrome_websites:
        factory.selenium(website in chrome_undetected_websites)
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


# local util methods
def title(factory: ExtendedFactory, types: Optional[List[str]] = None) -> ExtendedFactory:
    return factory.finder(f"{FINDER_NAME}_title_0", ByAttributesFinder, search_types=types or ["title"]).collector(
        f"{COLLECTOR_NAME}_title", FieldTypes.Text, [f"{FINDER_NAME}_title_0"]
    )


def text(
    factory: ExtendedFactory, clazz: str, holder_type: Optional[List[str]] = None, types: Optional[List[str]] = None
) -> ExtendedFactory:
    return (
        factory.finder(
            f"{FINDER_NAME}_text_0",
            ByAttributesFinder,
            search_types=holder_type or ["div"],
            search_limits={"class": clazz},
        )
        .finder(f"{FINDER_NAME}_text_1", ByAttributesFinder, search_types=types or ["p"])
        .collector(
            f"{COLLECTOR_NAME}_text",
            FieldTypes.Text,
            [f"{FINDER_NAME}_text_0", f"{FINDER_NAME}_text_1"],
            DEFAULT_POST_PROCESSINGS,
        )
    )


def orchestra(factory: ExtendedFactory) -> ExtendedFactory:
    return factory.orchestra([f"{COLLECTOR_NAME}_title", f"{COLLECTOR_NAME}_text"])


def link(
    factory: ExtendedFactory, clazz: str, holder_type: Optional[List[str]] = None, types: Optional[List[str]] = None
) -> ExtendedFactory:
    return (
        factory.finder(
            f"{FINDER_NAME}_link_0",
            ByAttributesFinder,
            search_types=holder_type or ["div"],
            search_limits={"class": clazz},
        )
        .finder(
            f"{FINDER_NAME}_link_1", ByAttributesFinder, search_types=types or ["a"], search_limits={"class": "next"}
        )
        .link_collector([f"{FINDER_NAME}_link_0", f"{FINDER_NAME}_link_1"])
    )


recognized_websites: List[str] = ["gravitytales.com"]
chrome_websites: List[str] = ["gravitytales.com"]
chrome_undetected_websites: List[str] = []
scroll_websites: Dict[str, Dict[str, Any]] = {}
block_screen_websites: Dict[str, Callable[[ExtendedFactory], Any]] = {
    "tl.rulate.ru": lambda factory: factory.finder(
        f"{FINDER_NAME}_block_0", ByAttributesFinder, search_types=["button"], search_limits={"name": "ok"}
    ).main_block_handler(ButtonClickHandler, button_finder=f"${FINDER_NAME}_block_0")
}
reload_websites: Dict[str, Dict[str, Any]] = {}
content_websites: Dict[str, Callable[[ExtendedFactory], Any]] = {}
link_websites: Dict[str, Callable[[ExtendedFactory], Any]] = {}


# FROM HERE BACKWARD COMPATIBILITY LIMITED SUPPORT

active_process_dicts = {
    "ranobehub.org": {"chrome": False},
    "jaomix.ru": {"chrome": False},
    "ranobes.com": {"chrome": True},
    "ranobes.net": {"chrome": True, "sleep": True},
    "ranobelib.me": {"chrome": True, "sleep": True},
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
    "18.foxaholic.com": {"chrome": True},
    "www.foxaholic.com": {
        "chrome": True,
        "wait": True,
    },
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
    "huitranslation.com": {},
    "ididmybesttranslations.wordpress.com": {},
    "kktranslates.home.blog": {"chrome": True, "wait": True},
    "gravitytales.com": {},
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
    "ranobelib.me": {
        "left": 0,
        "right": 0,
        "images": True,
        "text_h": "p",
        "text_l": {"class": "text-content"},
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"class": "wa_p"},
        "link_p": -1,
        "link_container": "div",
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
    "18.foxaholic.com": {
        "left": 0,
        "right": 0,
        "text_h": "p",
        "text_l": {"class": "text-left"},
        "title_h": "title",
        "title_l": None,
        "link_h": "a",
        "link_l": {"class": "next_page"},
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
    "chrysanthemumgarden.com": {
        "left": 0,
        "right": 0,
        "text_h": "p",
        "text_l": {"id": "novel-content"},
        "text_intelligent": True,
        "text_lang": ["eng"],
        "title_h": "title",
        "title_l": None,
        "link_h": "a",
        "link_l": {"class": "nav-next"},
        "images": True,
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
    "www.royalroad.com": {
        "text_h": "p",
        "text_l": {"class": "chapter-content"},
        "text_intelligent": True,
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"class": "nav-buttons"},
        "link_container": "div",
        "link_p": -1,
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
    "www.novelcool.com": {
        "text_h": "p",
        "text_l": {"class": "chapter-reading-section"},
        "title_h": "h2",
        "title_l": {"class": "chapter-title"},
        "link_h": "a",
        "link_l": {"class": "chapter-reading-pagination"},
        "link_container": "div",
        "link_p": -1,
    },
    "dummynovels.com": {
        "text_h": "p",
        "text_l": {"class": "elementor-widget-theme-post-content"},
        "title_h": "h1",
        "title_l": {"class": "chapter-heading"},
        "link_h": "a",
        "link_l": {"class": "chapter-nav-next"},
        "link_container": "div",
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
    "www.asianovel.net": {
        "text_h": "div",
        "text_l": {"data-dir": "ltr"},
        "text_container": "article",
        "title_h": "h2",
        "link_h": "a",
        "link_l": {"class": "pagination-single__right"},
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
    "novelhi.com": {
        "text_h": "sent",
        "text_l": {"id": "showReading"},
        "title_h": "h1",
        "title_l": {"class": "book_title"},
        "link_h": "a",
        "link_l": {"class": "next"},
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
    "novelbin.com": {
        "text_h": "p",
        "text_l": {"id": "chr-content"},
        "title_h": "h4",
        "link_h": "a",
        "link_l": {"id": "chr-nav-top"},
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
    "www.novelhall.com": {
        "text_l": {"id": "htmlContent"},
        "tags_used": ["br"],
        "title_h": "h1",
        "link_h": "a",
        "link_l": {"rel": "next"},
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
    "littlepinkstarfish.com": {
        "text_h": "p",
        "text_l": {"class": "entry-content"},
        "title_h": "h2",
        "link_h": "a",
        "link_l": {"rel": "next"},
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
    "gravitytales.com": {
        "text_h": "p",
        "text_l": {"id": "chapter-content"},
        "text_container": "section",
        "title_h": "h1",
        "link_h": "a",
        "link_container": "div",
        "link_l": {"class": "chapter__actions-right"},
        "link_p": -1,
    },
}

# === Auto-conversion from old settings to new structure ===
# Populate chrome/undetected/scroll/reload from active_process_dicts
for _site, _pcfg in active_process_dicts.items():
    if _pcfg.get("chrome"):
        if _site not in chrome_websites:
            chrome_websites.append(_site)
    if _pcfg.get("chrome_undetected"):
        if _site not in chrome_undetected_websites:
            chrome_undetected_websites.append(_site)
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
