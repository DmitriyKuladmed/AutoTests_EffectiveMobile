from __future__ import annotations

"""Глобальные фикстуры и хуки pytest.

Добавляет:
- `base_url` — базовый URL из переменной окружения;
- сбор логов браузера (console/response) и их вывод в HTML‑отчёт;
- колонку URL в таблице отчёта;
- авто‑открытие HTML‑отчёта после завершения прогона.
"""

import os
import shutil
from typing import Generator, Dict, List
import time
import webbrowser
from pathlib import Path

import pytest
try:
    from py.xml import html as pyhtml  # type: ignore
except Exception:  # pragma: no cover
    pyhtml = None


@pytest.fixture(scope="session")
def base_url() -> str:
    """Возвращает базовый URL (по умолчанию сайт компании)."""
    return os.getenv("BASE_URL", "https://effective-mobile.ru/").rstrip("/")


@pytest.fixture(autouse=True)
def _browser_logging(request: pytest.FixtureRequest, page) -> Generator[None, None, None]:
    """Собирает логи консоли и сетевые ответы для HTML‑отчёта."""
    if page is None:
        yield
        return

    console_messages: List[str] = []
    network_events: List[str] = []

    def on_console(msg):  # type: ignore[no-redef]
        try:
            console_messages.append(f"{msg.type}: {msg.text}")
        except Exception:
            pass

    def on_page_error(err):  # type: ignore[no-redef]
        try:
            console_messages.append(f"[Ошибка страницы]: {err}")
        except Exception:
            pass

    def on_response(resp):  # type: ignore[no-redef]
        try:
            network_events.append(f"{resp.status} {resp.url}")
        except Exception:
            pass

    page.on("console", on_console)
    page.on("pageerror", on_page_error)
    page.on("response", on_response)

    setattr(request.node, "_console_messages", console_messages)
    setattr(request.node, "_network_events", network_events)

    try:
        yield
    finally:
        try:
            page.off("console", on_console)
            page.off("pageerror", on_page_error)
            page.off("response", on_response)
        except Exception:
            pass

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Generator[None, None, None]:
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    page = item.funcargs.get("page") if hasattr(item, "funcargs") else None

    lines: List[str] = []
    if page:
        try:
            setattr(report, "_last_url", page.url)
            lines.append(f"URL: {page.url}")
        except Exception:
            pass

    console_messages = getattr(item, "_console_messages", None)
    if console_messages:
        lines.append("[Консоль]")
        lines.extend(console_messages)
    network_events = getattr(item, "_network_events", None)
    if network_events:
        lines.append("[Сеть]")
        lines.extend(network_events)
        total = len(network_events)
        success = 0
        client_err = 0
        server_err = 0
        other = 0
        for entry in network_events:
            try:
                status_str, _ = entry.split(" ", 1)
                status = int(status_str)
                if 200 <= status < 400:
                    success += 1
                elif 400 <= status < 500:
                    client_err += 1
                elif 500 <= status < 600:
                    server_err += 1
                else:
                    other += 1
            except Exception:
                other += 1
        lines.append("")
        lines.append(f"[Итого] всего={total}, успешных={success}, ошибки_клиента={client_err}, ошибки_сервера={server_err}, прочие={other}")

    try:
        setattr(report, "_combined_logs", "\n".join(lines))
    except Exception:
        pass


def pytest_html_results_table_header(cells):  
    if pyhtml is None:
        return
    cells.insert(2, pyhtml.th("URL"))


def pytest_html_results_table_row(report, cells):  
    if pyhtml is None:
        return
    url_text = getattr(report, "_last_url", "")
    cells.insert(2, pyhtml.td(url_text))


def pytest_html_results_table_html(report, data): 
    if pyhtml is None:
        return
    logs = getattr(report, "_combined_logs", "")
    if logs:
        data.clear()
        data.append(str(pyhtml.pre(logs)))


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Автоматически открывает HTML‑отчёт в браузере.

    Работает при запуске pytest с опцией --html=<путь> (pytest-html).
    Отключить можно через переменную окружения OPEN_REPORT=0.
    """
    if os.getenv("OPEN_REPORT", "1") == "0":
        return
    html_path = getattr(session.config.option, "htmlpath", None)
    if not html_path:
        return
    report_file = Path(html_path).resolve()
    if not report_file.exists():
        return
    time.sleep(0.2)
    try:
        webbrowser.open(report_file.as_uri(), new=2)
    except Exception:
        pass


def pytest_sessionstart(session: pytest.Session) -> None:
    """Очищает каталог allure-results перед стартом, если он остался от прошлых прогонов."""
    try:
        results_dir = Path(session.config.invocation_params.dir).joinpath("allure-results")
        if results_dir.exists():
            shutil.rmtree(results_dir, ignore_errors=True)
    except Exception:
        pass


