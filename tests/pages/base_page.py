from __future__ import annotations

"""Базовые помощники для Page Object.

Содержит общие действия: открытие URL, проверка попадания элемента во вьюпорт,
прокрутка к элементу. Используется наследниками.
"""

from typing import Optional

from playwright.sync_api import Page, Locator


class BasePage:
    """Базовый класс для всех страниц."""

    def __init__(self, page: Page, base_url: str) -> None:
        """Сохраняет страницу Playwright и базовый URL без завершающего слэша."""
        self.page: Page = page
        self.base_url: str = base_url.rstrip("/")

    def open(self, path: str = "") -> None:
        """Открывает базовый URL или путь относительно него."""
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        self.page.goto(url, wait_until="domcontentloaded")

    def is_locator_in_viewport(self, locator: Locator) -> bool:
        """Возвращает True, если элемент попадает во вьюпорт браузера."""
        self.page.wait_for_timeout(50)
        return self.page.evaluate(
            """
            (el) => {
                if (!el) return false;
                const rect = el.getBoundingClientRect();
                const vpH = window.innerHeight || document.documentElement.clientHeight;
                const vpW = window.innerWidth || document.documentElement.clientWidth;
                const verticallyVisible = rect.top < vpH && rect.bottom > 0;
                const horizontallyVisible = rect.left < vpW && rect.right > 0;
                return verticallyVisible && horizontallyVisible;
            }
            """,
            locator.element_handle(),
        )

    def scroll_into_view_if_needed(self, locator: Locator, timeout_ms: Optional[int] = 3000) -> None:
        """Прокручивает страницу к элементу при необходимости."""
        locator.scroll_into_view_if_needed(timeout=timeout_ms)


