from typing import Optional, List, Dict

from objects.builders.extended_factory import ExtendedFactory
from objects.elements.elements_finders import ByAttributesFinder
from objects.elements.elements_post_processings import ExactElementTaker, SplitTagContentByInnerTags
from objects.types.field_types import FieldTypes
from settings.builders_defaults import *


def simple_title(
    factory: ExtendedFactory, types: Optional[List[str]] = None, limits: Optional[Dict[str, str]] = None
) -> ExtendedFactory:
    return factory.finder(
        f"{FINDER_NAME}_title_0", ByAttributesFinder, search_types=types or ["title"], search_limits=limits or {}
    ).collector(f"{COLLECTOR_NAME}_title", FieldTypes.Text, [f"{FINDER_NAME}_title_0"], DEFAULT_POST_PROCESSINGS)


def simple_text(
    factory: ExtendedFactory,
    holder_type: List[str] = ["div"],
    holder_limit: Dict[str, str] = None,
    text_type: List[str] = ["p"],
    text_limit: Dict[str, str] = None,
    extra_post_processors: Optional[List[str]] = None,
) -> ExtendedFactory:
    return (
        factory.finder(
            f"{FINDER_NAME}_text_0",
            ByAttributesFinder,
            search_types=holder_type,
            search_limits=holder_limit or {},
        )
        .finder(f"{FINDER_NAME}_text_1", ByAttributesFinder, search_types=text_type, search_limits=text_limit or {})
        .collector(
            f"{COLLECTOR_NAME}_text",
            FieldTypes.Text,
            [f"{FINDER_NAME}_text_0", f"{FINDER_NAME}_text_1"],
            (extra_post_processors or []) + DEFAULT_POST_PROCESSINGS,
        )
    )


def split_text(
    factory: ExtendedFactory,
    holder_type: List[str] = ["div"],
    holder_limit: Dict[str, str] = None,
    split_by: List[str] = ["br"],
) -> ExtendedFactory:
    return (
        factory.finder(
            f"{FINDER_NAME}_text_0",
            ByAttributesFinder,
            search_types=holder_type,
            search_limits=holder_limit or {},
        )
        .post_processing(f"{POST_PROCESSING_NAME}_text_0", SplitTagContentByInnerTags, split_tag_names=split_by)
        .collector(
            f"{COLLECTOR_NAME}_text",
            FieldTypes.Text,
            [f"{FINDER_NAME}_text_0"],
            [f"{POST_PROCESSING_NAME}_text_0"] + DEFAULT_POST_PROCESSINGS,
        )
    )


def simple_link(
    factory: ExtendedFactory,
    holder_type: Optional[List[str]] = None,
    holder_limit: Dict[str, str] = None,
    link_type: Optional[List[str]] = None,
    link_limit: Dict[str, str] = None,
    link_exact: Optional[int] = None,
) -> ExtendedFactory:
    finders = []
    posts = []
    if holder_type:
        name = f"{FINDER_NAME}_link_{len(finders)}"
        finders.append(name)
        factory.finder(
            name,
            ByAttributesFinder,
            search_types=holder_type,
            search_limits=holder_limit or None,
        )
    if not link_type:
        raise RuntimeError("Incorrect function use")
    name = f"{FINDER_NAME}_link_{len(finders)}"
    finders.append(name)
    factory.finder(
        name,
        ByAttributesFinder,
        search_types=link_type,
        search_limits=link_limit,
    )
    if link_exact:
        name = f"{POST_PROCESSING_NAME}_link_{len(posts)}"
        posts.append(name)
        factory.post_processing(name, ExactElementTaker, take_at_index=link_exact)
    return factory.link_collector(finders, posts)


def orchestra(factory: ExtendedFactory, with_images: bool = False) -> ExtendedFactory:
    collectors = [f"{COLLECTOR_NAME}_title", f"{COLLECTOR_NAME}_text"]
    if with_images:
        collectors += [f"{COLLECTOR_NAME}_image"]
    return factory.orchestra(collectors)
