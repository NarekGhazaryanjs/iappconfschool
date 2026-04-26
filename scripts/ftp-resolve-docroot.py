#!/usr/bin/env python3
"""
Match public https://.../ to an FTP path by comparing index.html bytes.
Stdlib only. Writes dir= to GITHUB_OUTPUT (relative, trailing /).
"""
from __future__ import annotations

from collections import deque
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
_MAX_BFS_RETR = 100
_MAX_BFS_QUE = 500


def bfs_match_docroot(
    host: str,
    user: str,
    password: str,
    public: bytes,
    out_path: str,
) -> bool:
    """
    Search FTP for any index.html|htm under login root whose bytes == public.
    """
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
        try:
            for name, facts in ftp.mlsd():
                t = facts.get("type", "")
                if name in ("index.html", "index.htm") and t not in ("dir", "cdir", "pdir"):
                    files_here.append(name)
                elif t == "dir" and name not in (".", "..") and not name.startswith("."):
                    if name in _BFS_SKIP_DIRS:
                        continue
                    dirs_here.append(name)
        except Exception:
            try:
                for n in sorted(ftp.nlst()):
                    if n in (".", "..", ".htaccess", ".htpasswd") or n.startswith("."):
                        continue
                    if n in ("index.html", "index.htm"):
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

        for fname in files_here:
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

    print("::warning::No fixed candidate matched; BFS the FTP account for index.html …", file=sys.stderr)
    if bfs_match_docroot(host, user, password, public, out_path):
        return 0
    print(
        "::error::No index.html on this FTP (searched) matches the public home page. "
        "The domain may be served from another host or a non-HTML default (e.g. index.php).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
