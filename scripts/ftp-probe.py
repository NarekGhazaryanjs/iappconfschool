#!/usr/bin/env python3
"""
Finds FTP server-dir (relative) where uploaded files are served at https://opticssymposia.iapp.am/
Uses stdlib only. Writes discovered path to GITHUB_OUTPUT and prints for logs.
"""
from __future__ import annotations

import ftplib
import os
import random
import string
import sys
import time
import urllib.error
import urllib.request

BASE_URL = "https://opticssymposia.iapp.am"
PROBE_PREFIX = "gh-probe-"

# Segments: cwd each part in order (handles .. and nested paths)
CANDIDATES: list[tuple[str, ...]] = [
    ("public_html", "opticssymposia.iapp.am"),  # common cPanel: subdomain under public_html
    ("opticssymposia.iapp.am",),
    ("..", "opticssymposia.iapp.am"),
    ("public_html", "..", "opticssymposia.iapp.am"),
    ("domains", "opticssymposia.iapp.am", "public_html"),
    (".",),  # FTP sub-account: chrooted to vhost only — try last
]

MARKER = b"iappconfschool-probe-ok\n"


def main() -> int:
    host = os.environ.get("FTP_HOST", "").strip()
    user = os.environ.get("FTP_USER", "").strip()
    password = os.environ.get("FTP_PASS", "").strip()
    if not (host and user and password):
        print("::error::FTP_HOST, FTP_USER, FTP_PASS (from secrets) required", file=sys.stderr)
        return 1

    name = PROBE_PREFIX + "".join(random.choices(string.ascii_lowercase + string.digits, k=8)) + ".txt"
    out_path = os.environ.get("GITHUB_OUTPUT", "")

    for parts in CANDIDATES:
        # Server-dir for SamKirkland: use ../ style when we used ..
        if len(parts) == 1 and parts[0] == ".":
            server_dir = "./"
        else:
            server_dir = "/".join(parts) + "/"

        ftp: ftplib.FTP | None = None
        try:
            ftp = ftplib.FTP()
            ftp.connect(host, 21, timeout=45)
            ftp.login(user, password)
            ftp.set_pasv(True)
            for p in parts:
                ftp.cwd(p)
            from io import BytesIO

            bio = BytesIO(MARKER)
            ftp.storbinary(f"STOR {name}", bio)
            ftp.quit()
            ftp = None
        except Exception as e:
            if ftp:
                try:
                    ftp.close()
                except Exception:
                    pass
            print(f"probe-try: {server_dir!r} -> {e!r}", file=sys.stderr)
            continue

        time.sleep(2)
        url = f"{BASE_URL}/{name}"
        try:
            req = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
            body = urllib.request.urlopen(req, timeout=20).read()
        except urllib.error.URLError as e:
            print(f"probe-http: {url!r} -> {e!r}", file=sys.stderr)
            body = b""

        if MARKER.strip() in body or MARKER in body or b"probe-ok" in body:
            print(f"::notice::Discovered live FTP server-dir: {server_dir!r}")
            if out_path:
                with open(out_path, "a", encoding="utf-8") as go:
                    go.write(f"dir={server_dir}\n")
            # Remove probe from server
            try:
                ftp2 = ftplib.FTP()
                ftp2.connect(host, 21, timeout=45)
                ftp2.login(user, password)
                ftp2.set_pasv(True)
                for p in parts:
                    ftp2.cwd(p)
                try:
                    ftp2.delete(name)
                except Exception:
                    pass
                ftp2.quit()
            except Exception as e:
                print(f"probe-cleanup: {e!r}", file=sys.stderr)
            return 0

    # Do not guess: wrong path makes CI green but the real website stays stale.
    print(
        "::error::FTP probe: no candidate served probe file at "
        f"{BASE_URL!r} — set repository secret FTP_TARGET_DIR to the cPanel Subdomain "
        '"Document root" (relative to FTP home, e.g. public_html/opticssymposia.iapp.am/)',
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
