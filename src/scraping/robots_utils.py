import urllib.robotparser
import time
import requests
from src.utils.logger import logging

def check_robots_txt(base_url, target_path, user_agent="ResearchBot/1.0"):
    robots_url = f"{base_url}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        allowed = rp.can_fetch(user_agent, base_url + target_path)
        if allowed:
            logging.info(f"robots.txt allows scraping: {base_url + target_path}")
        else:
            logging.warning(f"robots.txt DISALLOWS scraping: {base_url + target_path}")
        return allowed
    except Exception as e:
        logging.error(f"Could not read robots.txt from {robots_url}: {e}")
        return True

HEADERS = {"User-Agent": "ResearchBot/1.0"}
DELAY = 1.5

def polite_get(url):
    time.sleep(DELAY)
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response