from __future__ import annotations

import random
import time
from urllib.parse import quote_plus

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _sleep(delay_range: tuple[float, float]) -> None:
    time.sleep(random.uniform(*delay_range))


def collect_place_links(
    driver: WebDriver,
    *,
    query: str,
    timeout_seconds: int,
    idle_retries: int,
    scroll_pause_range: tuple[float, float],
) -> list[str]:
    driver.get(f"https://www.google.com/maps/search/{quote_plus(query)}/")
    wait = WebDriverWait(driver, timeout_seconds)
    feed = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))

    last_height = driver.execute_script("return arguments[0].scrollHeight", feed)
    idle_count = 0

    while idle_count < idle_retries:
        driver.execute_script("arguments[0].scrollBy(0, arguments[0].scrollHeight);", feed)
        _sleep(scroll_pause_range)
        next_height = driver.execute_script("return arguments[0].scrollHeight", feed)
        if next_height == last_height:
            idle_count += 1
        else:
            idle_count = 0
        last_height = next_height

    hrefs: list[str] = []
    for anchor in feed.find_elements(By.XPATH, './/a[contains(@href,"/place/")]'):
        href = anchor.get_attribute("href")
        if href:
            hrefs.append(href)

    unique_hrefs: list[str] = []
    seen: set[str] = set()
    for href in hrefs:
        if href in seen:
            continue
        seen.add(href)
        unique_hrefs.append(href)

    return unique_hrefs
