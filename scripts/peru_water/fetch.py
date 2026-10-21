"""Download helpers with sha256 and polite rate limiting."""
from __future__ import annotations

import hashlib
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .paths import RAW_DIR, REQUEST_DELAY_SEC, USER_AGENT

_last_request_at = 0.0


@dataclass
class FetchResult:
    path: Path
    sha256: str
    bytes: int
    skipped: bool


def _throttle() -> None:
    global _last_request_at
    now = time.monotonic()
    wait = REQUEST_DELAY_SEC - (now - _last_request_at)
    if wait > 0:
        time.sleep(wait)
    _last_request_at = time.monotonic()


def _filename_for_url(url: str) -> str:
    path = urlparse(url).path
    name = Path(path).name or "download.bin"
    return name.replace("%20", "_")


def download(
    url: str,
    source_id: str,
    *,
    raw_dir: Path = RAW_DIR,
    max_bytes: int | None = None,
    force: bool = False,
    referer: str = "https://www.datosabiertos.gob.pe/",
    retries: int = 4,
) -> FetchResult:
    raw_dir.mkdir(parents=True, exist_ok=True)
    dest = raw_dir / source_id / _filename_for_url(url)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists() and not force:
        data = dest.read_bytes()
        if max_bytes is None or len(data) <= max_bytes:
            return FetchResult(dest, _sha256_bytes(data), len(data), True)

    headers = {"User-Agent": USER_AGENT, "Referer": referer}
    if max_bytes is not None:
        headers["Range"] = f"bytes=0-{max_bytes - 1}"

    if "datosabiertos.gob.pe" in url:
        return _download_curl(
            url, dest, max_bytes=max_bytes, retries=retries, referer=referer
        )

    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            _throttle()
            req = Request(url, headers=headers)
            with urlopen(req, timeout=180) as resp:
                data = resp.read()
            if max_bytes is not None and len(data) > max_bytes:
                data = data[:max_bytes]
            dest.write_bytes(data)
            return FetchResult(dest, _sha256_bytes(data), len(data), False)
        except Exception as exc:  # noqa: BLE001 — retry network/WAF flakes
            last_err = exc
            time.sleep(2 ** attempt)
    raise last_err  # type: ignore[misc]


def _download_curl(
    url: str,
    dest: Path,
    *,
    max_bytes: int | None,
    retries: int,
    referer: str,
) -> FetchResult:
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            _throttle()
            cmd = [
                "curl",
                "-fsSL",
                "-A",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "-e",
                referer,
                "--retry",
                "3",
                "--retry-delay",
                "2",
                "-o",
                str(dest),
            ]
            if max_bytes is not None:
                cmd.extend(["-r", f"0-{max_bytes - 1}"])
            cmd.append(url)
            subprocess.run(cmd, check=True, timeout=300)
            data = dest.read_bytes()
            return FetchResult(dest, _sha256_bytes(data), len(data), False)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(2 ** attempt)
    raise last_err  # type: ignore[misc]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def record_raw_file(conn, source_id: str, rel_path: str, sha256: str, nbytes: int, fetched_at: str) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO raw_files (source_id, rel_path, sha256, bytes, fetched_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (source_id, rel_path, sha256, nbytes, fetched_at),
    )
