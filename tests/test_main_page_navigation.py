from __future__ import annotations

"""UI‑тест главной страницы: проверка переходов по якорным ссылкам."""

from typing import List, Tuple

import pytest
from playwright.sync_api import Page, Locator

from .pages.main_page import MainPage


@pytest.mark.ui
def test_all_navigation_links_scroll_and_update_url(page: Page, base_url: str) -> None:
    """Открывает главную, кликает по всем якорным ссылкам и проверяет URL."""
    main = MainPage(page, base_url)
    main.open()

    pairs: List[Tuple[str, Locator]] = main.collect_unique_nav_links()
    assert pairs, "Не найдено ни одной якорной ссылки на странице"

    for expected, link_locator in pairs:
        target = main.click_nav_and_expect(expected, link_locator)
        assert target is not None


