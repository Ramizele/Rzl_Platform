from __future__ import annotations

import random
import re
import time
from urllib.parse import urlparse

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .browser import build_chrome_driver
from .config import FIELDNAMES, ScrappingConfig

RATING_RE = re.compile(r"([0-9]+(?:[\.,][0-9]+)?)")
INTEGER_RE = re.compile(r"(\d+)")
INSTAGRAM_HANDLE_RE = re.compile(r"@([A-Za-z0-9_.]{2,30})")


def _sleep(delay_range: tuple[float, float]) -> None:
    time.sleep(random.uniform(*delay_range))


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _safe_button_text(driver, item_id: str) -> str:
    try:
        raw = driver.find_element(By.XPATH, f'//button[contains(@data-item-id,"{item_id}")]').text
        return _clean_text(raw)
    except NoSuchElementException:
        return ""


def _extract_rating(driver) -> str:
    xpaths = (
        '//div[@role="img" and contains(@aria-label,"estrellas")]',
        '//div[@role="img" and contains(@aria-label,"stars")]',
    )
    for xpath in xpaths:
        try:
            aria_label = driver.find_element(By.XPATH, xpath).get_attribute("aria-label") or ""
            match = RATING_RE.search(aria_label)
            if match:
                return match.group(1).replace(",", ".")
        except NoSuchElementException:
            continue
    return ""


def _extract_comment_count(driver) -> str:
    xpaths = (
        '//*[contains(@class,"HHrUdb")]',
        '//button[contains(@aria-label,"rese")]',
        '//button[contains(@aria-label,"review")]',
    )
    for xpath in xpaths:
        try:
            text = driver.find_element(By.XPATH, xpath).text
            match = INTEGER_RE.search(text.replace(".", "").replace(",", ""))
            if match:
                return match.group(1)
        except NoSuchElementException:
            continue
    return ""


def _normalize_instagram_url(href: str) -> str:
    parsed = urlparse(href)
    path = parsed.path.strip("/")
    if not path:
        return "https://www.instagram.com/"

    first_segment = path.split("/")[0]
    if first_segment in {"p", "reel", "explore", "stories", "accounts"}:
        return href

    return f"https://www.instagram.com/{first_segment}/"


def _extract_instagram_or_web(driver) -> str:
    candidates: list[str] = []

    try:
        authority = driver.find_element(By.XPATH, '//a[contains(@data-item-id,"authority")]').get_attribute("href")
        if authority:
            candidates.append(authority.strip())
    except NoSuchElementException:
        pass

    for anchor in driver.find_elements(By.XPATH, '//a[contains(@href,"instagram.com")]'):
        href = anchor.get_attribute("href")
        if href:
            candidates.append(href.strip())

    for href in candidates:
        if "instagram.com" in href.lower():
            return _normalize_instagram_url(href)

    if candidates:
        return candidates[0]

    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text
        handle_match = INSTAGRAM_HANDLE_RE.search(page_text)
        if handle_match:
            return f"https://www.instagram.com/{handle_match.group(1)}/"
    except NoSuchElementException:
        pass

    return ""


def _extract_status(driver) -> str:
    try:
        element = driver.find_element(
            By.XPATH,
            "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'cerrado temporalmente')"
            " or contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'temporarily closed')"
            " or contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'cerrado permanentemente')"
            " or contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'closed permanently')]",
        )
        text = (element.text or "").lower()
        if "cerrado temporalmente" in text or "temporarily closed" in text:
            return "Cerrado temporalmente"
        if "cerrado permanentemente" in text or "closed permanently" in text:
            return "Cerrado permanentemente"
    except NoSuchElementException:
        return ""

    return ""


def infer_barrio(query: str) -> str:
    stopwords = {
        "bares",
        "bar",
        "pub",
        "pubs",
        "cerveceria",
        "cervecerias",
        "buenos",
        "aires",
        "caba",
        "zona",
        "en",
        "de",
        "la",
    }
    tokens = [token for token in re.split(r"\s+", query.lower()) if token and token not in stopwords]
    if not tokens:
        return ""
    return " ".join(token.capitalize() for token in tokens)


def scrape_place(href: str, query: str, config: ScrappingConfig) -> dict[str, str]:
    row = {field: "" for field in FIELDNAMES}
    row["Link Maps"] = href
    row["Query"] = query
    row["Barrio"] = infer_barrio(query)

    user_agent = random.choice(tuple(config.user_agents)) if config.user_agents else None
    driver = build_chrome_driver(headless=config.headless_workers, user_agent=user_agent)

    try:
        wait = WebDriverWait(driver, config.timeout_seconds)
        driver.get(href)
        _sleep(config.place_load_delay_range)

        row["Nombre"] = _clean_text(
            wait.until(EC.presence_of_element_located((By.XPATH, '//h1[contains(@class,"DUwDvf")]'))).text
        )
        row["Direccion"] = _safe_button_text(driver, "address")
        row["Telefono"] = _safe_button_text(driver, "phone")
        row["Estrellas"] = _extract_rating(driver)
        row["Comentarios"] = _extract_comment_count(driver)
        row["Instagram_o_Web"] = _extract_instagram_or_web(driver)
        row["Estado"] = _extract_status(driver)

        _sleep(config.request_delay_range)
    except TimeoutException:
        return row
    finally:
        driver.quit()

    return row
