#!/usr/bin/env python3
"""
Match public https://.../ to an FTP path by comparing index.html bytes.
Stdlib only. Writes dir= to GITHUB_OUTPUT (relative, trailing /).
"""
from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
import email.utils
import ftplib
from io import BytesIO
import os
import re
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


def _ts_close(a: datetime, b: datetime) -> bool:
    if a.tzinfo is None:
        a = a.replace(tzinfo=timezone.utc)
    if b.tzinfo is None:
        b = b.replace(tzinfo=timezone.utc)
    return abs((a.astimezone(timezone.utc) - b.astimezone(timezone.utc)).total_seconds()) <= 3.0


def _ftp_size(ftp: ftplib.FTP, name: str) -> int | None:
    try:
        line = ftp.sendcmd(f"SIZE {name}")
    except Exception:
        return None
    m = re.search(r"213\s+(\d+)", line or "")
    if m:
        return int(m.group(1))
    return None


def _ftp_mdtm(ftp: ftplib.FTP, name: str) -> datetime | None:
    try:
        line = ftp.sendcmd(f"MDTM {name}")
    except Exception:
        return None
    m = re.search(
        r"213\s+(\d{4})(\d{2})(\d{2})(?:(\d{2})(\d{2})(\d{2}))?",
        line or "",
    )
    if not m:
        return None
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if m.group(4) is not None:
        h, mi, s = int(m.group(4)), int(m.group(5)), int(m.group(6))
    else:
        h, mi, s = 0, 0, 0
    return datetime(y, mo, d, h, mi, s, tzinfo=timezone.utc)


def _http_last_modified_to_dt(lm: str) -> datetime | None:
    try:
        t = email.utils.parsedate_to_datetime(lm)
    except (TypeError, ValueError, OverflowError):
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return t.astimezone(timezone.utc)


def _parts_to_dir(parts: tuple[str, ...]) -> str:
    if not parts:
        return "./"
    s = "/".join(parts) + "/"
    return s


_BFS_SKIP_DIRS = frozenset(
    {
        "node_modules",
        "cgi-bin",
        ".trash",
        "logs",
        "Maildir",
        "etc",
        "ssl",
        "tmp",
    }
)
_MAX_BFS_DEPTH = 8
_MAX_BFS_RETR = 200
_MAX_BFS_QUE = 500


def bfs_match_docroot(
    host: str,
    user: str,
    password: str,
    public: bytes,
    out_path: str,
    http_last_modified: datetime | None = None,
) -> bool:
    """
    Search FTP: any .html/.htm in tree matching public bytes; also MDTM for index names.
    """
    target_len = len(public)
    n_retr = 0
    q: deque[tuple[str, ...]] = deque()
    q.append(())
    enqueued: set[tuple[str, ...]] = {()}

    while q and n_retr < _MAX_BFS_RETR:
        parts = q.popleft()
        if len(parts) > _MAX_BFS_DEPTH:
            continue

        try:
            ftp = ftplib.FTP()
            ftp.connect(host, 21, timeout=50)
            ftp.login(user, password)
            ftp.set_pasv(True)
            for p in parts:
                if p == "..":
                    ftp.cwd("..")
                else:
                    ftp.cwd(p)
        except Exception as e:
            print(f"bfs open {parts!r}: {e!r}", file=sys.stderr)
            continue

        files_here: list[str] = []
        dirs_here: list[str] = []
        mlsd_sizes: dict[str, int | None] = {}
        used_mlsd = False
        try:
            for name, facts in ftp.mlsd():
                t = facts.get("type", "")
                lname = name.lower()
                if t == "file" and lname.endswith((".html", ".htm")):
                    files_here.append(name)
                    szr = facts.get("size")
                    if str(szr or "").isdigit():
                        mlsd_sizes[name] = int(str(szr))
                    else:
                        mlsd_sizes[name] = None
                elif t == "dir" and name not in (".", "..") and not name.startswith("."):
                    if name in _BFS_SKIP_DIRS:
                        continue
                    dirs_here.append(name)
            used_mlsd = True
        except Exception:
            try:
                for n in sorted(ftp.nlst()):
                    if n in (".", "..", ".htaccess", ".htpasswd") or n.startswith("."):
                        continue
                    nlow = n.lower()
                    if nlow.endswith((".html", ".htm")):
                        files_here.append(n)
                    else:
                        if n in _BFS_SKIP_DIRS:
                            continue
                        try:
                            ftp.cwd(n)
                            ftp.cwd("..")
                            dirs_here.append(n)
                        except Exception:
                            pass
            except Exception as e2:
                print(f"bfs list {parts!r}: {e2!r}", file=sys.stderr)
                try:
                    ftp.close()
                except Exception:
                    pass
                continue

        seenf: set[str] = set()
        uniq: list[str] = []
        for f in files_here:
            if f not in seenf:
                seenf.add(f)
                uniq.append(f)
        files_here = uniq

        for fname in files_here:
            if http_last_modified is not None:
                t = _ftp_mdtm(ftp, fname)
                if t is not None and _ts_close(t, http_last_modified):
                    d = _parts_to_dir(parts)
                    print(
                        f"::notice::BFS: MDTM+HTTP Last-Modified match {fname} under {d!r} — use this for deploy"
                    )
                    if out_path:
                        with open(out_path, "a", encoding="utf-8") as go:
                            go.write(f"dir={d}\n")
                    try:
                        ftp.close()
                    except Exception:
                        pass
                    return True
            sz = mlsd_sizes.get(fname) if used_mlsd else None
            if sz is None:
                sz = _ftp_size(ftp, fname)
            if sz is not None and sz != target_len:
                continue
            if n_retr >= _MAX_BFS_RETR:
                break
            n_retr += 1
            buf = BytesIO()
            try:
                ftp.retrbinary(f"RETR {fname}", buf.write, blocksize=65536)
            except Exception:
                continue
            if _norm(buf.getvalue()) == public:
                d = _parts_to_dir(parts)
                print(
                    f"::notice::BFS: public page matches {fname} under {d!r} — use this for deploy"
                )
                if out_path:
                    with open(out_path, "a", encoding="utf-8") as go:
                        go.write(f"dir={d}\n")
                try:
                    ftp.close()
                except Exception:
                    pass
                return True

        for name in dirs_here:
            child = (*parts, name)
            if child not in enqueued and len(q) < _MAX_BFS_QUE:
                enqueued.add(child)
                q.append(child)

        try:
            ftp.close()
        except Exception:
            pass

    if n_retr > 0:
        print(
            f"::warning::BFS tried {n_retr} index files, no public match",
            file=sys.stderr,
        )
    return False


def _fetch_public_and_last_modified() -> tuple[bytes, datetime | None]:
    req = urllib.request.Request(
        BASE,
        headers={"User-Agent": "iappconfschool-ci", "Cache-Control": "no-cache"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read()
        raw_lm = r.headers.get("Last-Modified")
    if not raw_lm:
        return _norm(body), None
    dtlm = _http_last_modified_to_dt(raw_lm)
    return _norm(body), dtlm


def main() -> int:
    host = os.environ["FTP_HOST"].strip()
    user = os.environ["FTP_USER"].strip()
    password = os.environ["FTP_PASS"].strip()
    out_path = os.environ.get("GITHUB_OUTPUT", "")

    try:
        public, http_lm = _fetch_public_and_last_modified()
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
            if http_lm is not None:
                for fname in ("index.html", "index.htm"):
                    t = _ftp_mdtm(ftp, fname)
                    if t is not None and _ts_close(t, http_lm):
                        print(
                            f"::notice::MDTM matches HTTP Last-Modified at {server_dir!r} ({fname})"
                        )
                        if out_path:
                            with open(out_path, "a", encoding="utf-8") as go:
                                go.write(f"dir={server_dir}\n")
                        try:
                            ftp.close()
                        except Exception:
                            pass
                        return 0
            buf = BytesIO()
            try:
                ftp.retrbinary("RETR index.html", buf.write, blocksize=65536)
            except Exception:
                try:
                    buf = BytesIO()
                    ftp.retrbinary("RETR index.htm", buf.write, blocksize=65536)
                except Exception:
                    try:
                        ftp.close()
                    except Exception:
                        pass
                    continue
            raw = buf.getvalue()
            try:
                ftp.close()
            except Exception:
                pass
        except Exception as e:
            print(f"try {server_dir!r}: {e!r}", file=sys.stderr)
            continue

        if _norm(raw) == public:
            print(
                f"::notice::Live index (bytes) matches FTP path: {server_dir!r} — this is the real document root for deploy"
            )
            if out_path:
                with open(out_path, "a", encoding="utf-8") as go:
                    go.write(f"dir={server_dir}\n")
            return 0

    print("::warning::No fixed candidate matched; BFS the FTP account for index.html …", file=sys.stderr)
    if bfs_match_docroot(host, user, password, public, out_path, http_lm):
        return 0
    print(
        "::error::No index.html on this FTP (searched) matches the public home page. "
        "The domain may be served from another host or a non-HTML default (e.g. index.php).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
