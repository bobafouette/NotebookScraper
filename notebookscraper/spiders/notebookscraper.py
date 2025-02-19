import logging
import os
import scrapy
import tomli
import w3lib

from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from urllib.parse import urlparse, urlsplit

MAX_FILE_SIZE = 500000


class NotebookScraper(scrapy.Spider):
    name = "quotes"
    # start_urls = [
    #     "https://docs.astral.sh/uv/",
    # ]

    def start_requests(self):
        self.hosts = []
        for url in getattr(self, "config", {}).keys():
            self.hosts.append(urlparse(url).netloc)
            yield scrapy.Request(url, self.parse)

    def extract_content(self, response, url_config):
        body = ""
        for content_selector in url_config.get("content-selector", ["body > p"]):
            logging.debug(f"Extracting content from '{content_selector}'")
            content = response.css(content_selector).get()
            if not content or content in body:
                continue
            body += content + "\n"

        if not body:
            return

        body = w3lib.html.remove_tags(body)
        clean_body = ""
        for line in body.split("\n"):
            line = line.strip()
            if not line:
                continue
            clean_body += line + "\n"
        return clean_body

    def save_content(self, clean_body, url):
        split_url = urlsplit(url)
        hostname = split_url.netloc
        if self.split:
            content_file_name_base = (
                f"{hostname}_{split_url.path.replace('/', '_').replace(':', '_')}"
            )
        else:
            content_file_name_base = f"{hostname}"

        file_counter = 0
        for content_file in os.listdir(self.output):
            if not content_file.startswith(content_file_name_base):
                continue
            file_counter += 1

        if file_counter > 1:
            content_file_path = (
                f"{self.output}/{content_file_name_base}_{file_counter}.txt"
            )
        else:
            content_file_path = f"{self.output}/{content_file_name_base}.txt"

        skipwriting = False
        if os.path.exists(content_file_path):

            with open(f"{content_file_path}", "r") as html_txt:
                content_file_content = html_txt.read()
                if clean_body in content_file_content:
                    skipwriting = True
                elif len(content_file_content.split("\n")) >= MAX_FILE_SIZE:
                    file_counter += 1
                    content_file_path = (
                        f"{self.output}/{content_file_name_base}_{file_counter}.txt"
                    )

        if not skipwriting:
            with open(f"{content_file_path}", "a") as html_txt:
                logging.info(f"Writing to {content_file_path}")
                html_txt.write(clean_body)

    def parse(self, response):
        url = response.url
        for configured_url in self.config:
            split_url = urlsplit(configured_url)
            base_url = f"{split_url.scheme}://{split_url.netloc}"
            logging.debug(f"Checking if '{url}' starts with '{base_url}'")
            if not url.startswith(base_url):
                continue
            url_config = self.config.get(configured_url)
            break
        else:
            raise ValueError(f"Could not find a config section for '{url}'")

        hostname = urlparse(url).netloc
        if hostname not in self.hosts:
            return

        clean_body = self.extract_content(response, url_config)
        if clean_body:
            self.save_content(clean_body, url)

        for link_selector in url_config.get("link-selector", []):
            logging.debug(f"Looking for selector: {link_selector}")
            page_links = response.css(link_selector)
            logging.info(f"Following links: {page_links}")
            yield from response.follow_all(page_links, self.parse)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="doc-scraper", description="Crawl & extract text from web site"
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Path to a configuration file ('./doc-scraper.toml' by default)",
        default="./doc-scraper.toml",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Path to the output directory ('/tmp/scrapper' by default)",
        default="/tmp/scrapper",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="Enable verbose output",
        action="store_true",
    )

    parser.add_argument(
        "-s",
        "--split",
        help="Split output files by url. Default is to append to the same file all the link of the same domain.",
        action="store_true",
    )

    args = parser.parse_args()

    if args.config:
        config_path = args.config
    else:
        config_path = "./doc-scraper.toml"

    # Check if the config file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file '{config_path}' not found")

    # Check if the output directory exists
    if not os.path.exists(args.output):

        # If it does not exist, does the parent directory exist?
        if not os.path.exists(os.path.dirname(args.output)):
            raise FileNotFoundError(
                f"Output directory '{os.path.dirname(args.output)}' not found"
            )

        # If the parent directory exists, create the output directory
        os.makedirs(args.output)

    with open(config_path, mode="rb") as config_file:
        config = tomli.load(config_file)

    if args.verbose:
        logging.info("Verbose output enabled")
        logging.basicConfig(level=logging.WARNING)
        log_level = logging.DEBUG
    else:
        logging.basicConfig(level=logging.WARNING)
        log_level = logging.INFO

    configure_logging({"LOG_LEVEL": log_level})
    process = CrawlerProcess()
    process.crawl(NotebookScraper, config=config, output=args.output, split=args.split)
    process.start()


if __name__ == "__main__":
    main()
