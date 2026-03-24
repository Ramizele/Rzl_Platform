from __future__ import annotations

from functools import lru_cache

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@lru_cache(maxsize=1)
def _chromedriver_binary() -> str:
    return ChromeDriverManager().install()


def build_chrome_driver(*, headless: bool, user_agent: str | None = None) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")
    options.add_argument("--lang=es-AR")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)

    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

    service = Service(_chromedriver_binary())
    return webdriver.Chrome(service=service, options=options)
