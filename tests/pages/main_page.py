from __future__ import annotations

"""Page Object для главной страницы https://effective-mobile.ru.

Собирает якорные ссылки и проверяет переходы по ним.
"""

from typing import List, Tuple
from urllib.parse import urlsplit
from playwright.sync_api import Locator, Page

from .base_page import BasePage


class MainPage(BasePage):
    """Главная страница: навигация по якорям."""

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)

        self._header_selectors = [
            'header nav a[href]',
            'header .t-menu a[href]',
            'header .t228__menu a[href]',
            'header a.t-menu__link-item[href]',
            'header a[href]',
        ]
        self.all_links: Locator = page.locator('a[href]')

    def collect_unique_nav_links(self) -> List[Tuple[str, Locator]]:
        """Возвращает список уникальных ссылок-«якорей» в виде пар
        (фрагмент, локатор). Всплывающие окна и невидимые элементы отбрасываются.
        """
        links: List[Tuple[str, Locator]] = []
        seen: set[str] = set()

        candidate = self.page.locator('a[href*="#"]')

        count = candidate.count()
        for idx in range(count):
            loc = candidate.nth(idx)
            href = loc.get_attribute("href") or ""
            if not href or href.startswith(("mailto:", "tel:")):
                continue
            if href.startswith("javascript:"):
                continue
            if "popup:" in href:
                continue
            if not loc.is_visible():
                continue

            parsed = urlsplit(href)
            fragment = f"#{parsed.fragment}" if parsed.fragment else ""
            if not fragment:
                continue
            if "popup:" in fragment:
                continue
            expected = fragment

            if expected in seen:
                continue
            if expected in {"/", "/#", "/#top", "#", "#top"}:
                continue
            seen.add(expected)
            links.append((expected, loc))

        return links

    def click_nav_and_expect(self, expected_path_or_fragment: str, link_locator: Locator) -> Locator:
        """Кликает по ссылке и проверяет наличие ожидаемого фрагмента в URL.

        Возвращает локатор целевой секции (или основного контента).
        """
        link_locator.scroll_into_view_if_needed()
        link_locator.click(button="left")
        try:
            self.page.wait_for_function(
                "exp => window.location.href.includes(exp)",
                expected_path_or_fragment,
                timeout=2000,
            )
        except Exception:
            self.page.wait_for_timeout(300)

        assert expected_path_or_fragment in self.page.url, (
            f"URL не содержит ожидаемое '{expected_path_or_fragment}': {self.page.url}"
        )

        if expected_path_or_fragment.startswith('#'):
            target_id = expected_path_or_fragment[1:]
            content = self.page.locator(
                f'[id="{target_id}"], a[name="{target_id}"], '
                f'[*|data-anchor="{target_id}"], [data-menu-anchor="{target_id}"]'
            )
            assert content.count() > 0, f"Не найдена секция {expected_path_or_fragment}"
            self.scroll_into_view_if_needed(content.first)
            return content.first
        content = self.page.locator("main, h1").first
        assert content.is_visible(), "Ожидался видимый контент страницы"
        return content


