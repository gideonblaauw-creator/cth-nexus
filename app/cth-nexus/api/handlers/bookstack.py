import os
import time
import logging

import requests

BOOKSTACK_URL = os.environ.get("BOOKSTACK_URL", "https://wiki.cleantechhub.net")
BOOKSTACK_TOKEN = os.environ.get("BOOKSTACK_TOKEN", "")

log = logging.getLogger("cth-mentor-api.bookstack")

_last_request_time = 0.0


class BookStackClient:

    def __init__(self, base_url=None, token=None):
        self.base_url = (base_url or BOOKSTACK_URL).rstrip("/")
        self.token = token or BOOKSTACK_TOKEN
        if not self.token:
            log.warning("BOOKSTACK_TOKEN not set — API calls will fail")

    def _headers(self):
        return {"Authorization": f"Token {self.token}"}

    def _request(self, method, path, **kwargs):
        global _last_request_time
        elapsed = time.time() - _last_request_time
        if elapsed < 0.5:
            time.sleep(0.5 - elapsed)

        url = f"{self.base_url}/api/{path.lstrip('/')}"
        resp = requests.request(method, url, headers=self._headers(), timeout=30, **kwargs)
        _last_request_time = time.time()

        if resp.status_code == 429:
            retry_after = float(resp.headers.get("Retry-After", 2))
            log.warning("Rate limited, retrying after %.1fs", retry_after)
            time.sleep(retry_after)
            resp = requests.request(method, url, headers=self._headers(), timeout=30, **kwargs)
            _last_request_time = time.time()

        resp.raise_for_status()
        return resp.json() if resp.content else {}

    def get_page(self, page_id):
        return self._request("GET", f"pages/{page_id}")

    def list_pages(self, count=100, offset=0, filters=None):
        params = {"count": count, "offset": offset}
        if filters:
            params.update(filters)
        return self._request("GET", "pages", params=params)

    def search(self, query, page=1, count=100):
        return self._request("GET", "search", params={
            "query": query, "page": page, "count": count,
        })

    def update_page_tags(self, page_id, tags):
        return self._request("PUT", f"pages/{page_id}", json={"tags": tags})

    def list_pages_by_tag(self, tag_name, tag_value=None):
        query = f"[{tag_name}={tag_value}]" if tag_value else f"[{tag_name}]"
        results = []
        page = 1
        while True:
            resp = self.search(query, page=page)
            results.extend(resp.get("data", []))
            if len(results) >= resp.get("total", 0):
                break
            page += 1
        return results
