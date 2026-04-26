#!/usr/bin/env python3
"""
Match public https://.../ to an FTP path by comparing index.html bytes.
Stdlib only. Writes dir= to GITHUB_OUTPUT (relative, trailing /).
"""
from __future__ import annotations

import ftplib
from io import BytesIO
import os
import sys
import urllib.error
import urllib.request

BASE = "https://opticssymposia.iapp.am/"

# Tuples of CWD parts after login; () = never cwd from login home.
# Covers typical cPanel + sibling folders, public_html, domains/*.
CANDIDATES: list[tuple[str, ...]] = [
    (),
    ("opticssymposia.iapp.am",),
    ("opticssymposia",),
    ("subdomains", "opticssymposia.iapp.am"),
    ("subdomains", "opticssymposia"),
    ("public_html", "opticssymposia"),
    ("public_html", "opticssymposia.iapp.am"),
    ("public_html",),
    ("domains", "opticssymposia.iapp.am", "public_html"),
    ("www", "opticssymposia.iapp.am"),
    ("htdocs", "opticssymposia.iapp.am"),
    ("httpdocs", "opticssymposia.iapp.am"),
    ("..", "opticssymposia.iapp.am"),
    ("..", "public_html", "opticssymposia.iapp.am"),
    ("..", "public_html", "opticssymposia"),
    ("..", "subdomains", "opticssymposia.iapp.am"),
]


def _norm(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n")


def _parts_to_dir(parts: tuple[str, ...]) -> str:
    if not parts:
        return "./"
    s = "/".join(parts) + "/"
    return s


def _fetch_public() -> bytes:
    req = urllib.request.Request(BASE, headers={"User-Agent": "iappconfschool-ci", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main() -> int:
    host = os.environ["FTP_HOST"].strip()
    user = os.environ["FTP_USER"].strip()
    password = os.environ["FTP_PASS"].strip()
    out_path = os.environ.get("GITHUB_OUTPUT", "")

    try:
        public = _norm(_fetch_public())
    except urllib.error.URLError as e:
        print(f"::error::Cannot fetch {BASE}: {e!r}", file=sys.stderr)
        return 1

    for parts in CANDIDATES:
        server_dir = _parts_to_dir(parts)
        try:
            ftp = ftplib.FTP()
            ftp.connect(host, 21, timeout=45)
            ftp.login(user, password)
            ftp.set_pasv(True)
            for p in parts:
                if p == "..":
                    ftp.cwd("..")
                else:
                    ftp.cwd(p)
            buf = BytesIO()
            try:
                ftp.retrbinary("RETR index.html", buf.write, blocksize=65536)
            except Exception:
                try:
                    ftp.close()
                except Exception:
                    pass
                continue
            raw = buf.getvalue()
            ftp.close()
        except Exception as e:
            print(f"try {server_dir!r}: {e!r}", file=sys.stderr)
            continue

        if _norm(raw) == public:
            print(f"::notice::Live index matches FTP path: {server_dir!r} — this is the real document root for deploy")
            if out_path:
                with open(out_path, "a", encoding="utf-8") as go:
                    go.write(f"dir={server_dir}\n")
            return 0

    print(
        "::error::No FTP path in candidate list has the same index.html as the public site. "
        "The site or FTP may use a different account.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
