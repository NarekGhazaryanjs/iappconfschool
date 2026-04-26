#!/usr/bin/env python3
"""Download index.html from remote FTP (same path as deploy) and check for a marker. Stdlib only."""
from __future__ import annotations

import ftplib
import os
import sys


def main() -> int:
    host = os.environ["FTP_HOST"].strip()
    user = os.environ["FTP_USER"].strip()
    password = os.environ["FTP_PASS"].strip()
    server_dir = os.environ.get("SERVER_DIR", "./").strip()
    if not server_dir.endswith("/"):
        server_dir += "/"

    ftp = ftplib.FTP()
    ftp.connect(host, 21, timeout=40)
    ftp.login(user, password)
    ftp.set_pasv(True)
    for p in server_dir.strip("/").split("/"):
        if not p or p == ".":
            continue
        if p == "..":
            ftp.cwd("..")
        else:
            ftp.cwd(p)
    try:
        lines: list[bytes] = []
        def cb(chunk: bytes) -> None:
            lines.append(chunk)
        ftp.retrbinary("RETR index.html", cb, blocksize=65536)
    except Exception as e:
        print(f"::error::RETR index.html: {e!r}", file=sys.stderr)
        return 1
    body = b"".join(lines)
    ftp.quit()

    m = b"iappconfschool-deploy: active"
    if m in body:
        print("::notice::Remote index.html contains deploy marker (FTP read OK).")
        return 0
    print("::error::Remote index.html (via FTP) has no iappconfschool-deploy marker.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
