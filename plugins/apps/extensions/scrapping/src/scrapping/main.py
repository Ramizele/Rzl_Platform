from __future__ import annotations

import argparse
import logging
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .browser import build_chrome_driver
from .config import FIELDNAMES, ScrappingConfig
from .dedup import add_known_place, load_known_places, persist_known_places
from .queries import load_queries
from .scraper_feed import collect_place_links
from .scraper_place import scrape_place
from .storage import append_rows

LOGGER = logging.getLogger("scrapping")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scrape bars from Google Maps using query list.")
    parser.add_argument("--queries-file", type=Path, help="Override queries text file.")
    parser.add_argument("--output-csv", type=Path, help="Override output CSV path.")
    parser.add_argument("--duplicates-csv", type=Path, help="Override dedupe CSV path.")
    parser.add_argument("--max-workers", type=int, default=4, help="Parallel workers for place scraping.")
    parser.add_argument("--headless-feed", action="store_true", help="Run feed browser in headless mode.")
    parser.add_argument("--visible-workers", action="store_true", help="Run workers in visible mode.")
    parser.add_argument("--timeout", type=int, default=12, help="Wait timeout in seconds.")
    return parser


def _build_config(args: argparse.Namespace) -> ScrappingConfig:
    config = ScrappingConfig()

    if args.queries_file:
        config.queries_file = args.queries_file
    if args.output_csv:
        config.output_csv = args.output_csv
    if args.duplicates_csv:
        config.duplicates_csv = args.duplicates_csv

    requested_workers = max(1, args.max_workers)
    config.max_workers = min(requested_workers, 4)
    config.timeout_seconds = max(5, args.timeout)
    config.headless_feed = bool(args.headless_feed)
    config.headless_workers = not bool(args.visible_workers)

    if requested_workers > 4:
        LOGGER.warning("max_workers capped to 4 to reduce blocking risk on Google Maps.")

    config.ensure_output_paths()
    return config


def _collect_links_for_query(query: str, config: ScrappingConfig) -> list[str]:
    user_agent = random.choice(tuple(config.user_agents)) if config.user_agents else None
    driver = build_chrome_driver(headless=config.headless_feed, user_agent=user_agent)
    try:
        return collect_place_links(
            driver,
            query=query,
            timeout_seconds=config.timeout_seconds,
            idle_retries=config.scroll_idle_retries,
            scroll_pause_range=config.feed_scroll_pause_range,
        )
    finally:
        driver.quit()


def run(config: ScrappingConfig) -> int:
    queries = load_queries(config.queries_file)
    known_places = load_known_places(config.duplicates_csv)

    LOGGER.info("Loaded %d queries from %s", len(queries), config.queries_file)
    LOGGER.info("Loaded %d known records for dedupe", len(known_places))

    for query in queries:
        LOGGER.info("Searching query: %s", query)
        links = _collect_links_for_query(query, config)
        LOGGER.info("Found %d place links", len(links))

        if not links:
            continue

        new_rows: list[dict[str, str]] = []
        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            futures = {executor.submit(scrape_place, href, query, config): href for href in links}
            for future in as_completed(futures):
                href = futures[future]
                try:
                    row = future.result()
                except Exception as exc:  # defensive logging for flaky browser sessions
                    LOGGER.warning("Failed scraping %s: %s", href, exc)
                    continue

                if add_known_place(known_places, row):
                    new_rows.append(row)
                    LOGGER.info("Added: %s", row.get("Nombre") or href)

        added = append_rows(config.output_csv, rows=new_rows, fieldnames=FIELDNAMES)
        persist_known_places(config.duplicates_csv, known_places)
        LOGGER.info("Rows written for query '%s': %d", query, added)

    LOGGER.info("Scrapping run finished.")
    return 0


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    args = _build_parser().parse_args()
    config = _build_config(args)
    return run(config)


if __name__ == "__main__":
    raise SystemExit(main())
