"""Stamp published footers with the month of the latest website content change."""

import argparse
from datetime import datetime
from pathlib import Path
import hashlib
import re
import subprocess
from zoneinfo import ZoneInfo


FOOTER = re.compile(
    r'(<div class="nav-footer-center">\s*<p>)(.*?)(</p>\s*</div>)',
    re.DOTALL,
)


def update_footers(site_dir: Path, updated_at: str) -> int:
    timestamp = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("The site update timestamp must include a timezone.")
    updated = timestamp.astimezone(ZoneInfo("America/Los_Angeles"))
    signature = f"© {updated.year} Daihong Min · Last updated {updated:%B %Y}"
    pages = []
    for path in sorted(site_dir.rglob("*.html")):
        content = path.read_bytes().decode("utf-8")
        if '<footer class="footer">' not in content:
            continue
        matches = list(FOOTER.finditer(content))
        if len(matches) != 1 or "Last updated" not in matches[0].group(2):
            raise ValueError(f"Expected one update-date footer in {path}.")
        result = FOOTER.sub(lambda m: m.group(1) + signature + m.group(3), content)
        pages.append((path, result))
    if not pages:
        raise ValueError(f"No website footers found in {site_dir}.")
    for path, content in pages:
        path.write_bytes(content.encode("utf-8"))
    print(f"{signature} ({len(pages)} pages; America/Los_Angeles)")
    return len(pages)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, default=Path("docs"))
    parser.add_argument("--updated-at", help="ISO timestamp; defaults to the latest docs commit.")
    args = parser.parse_args()
    updated_at = args.updated_at or subprocess.check_output(
        ["git", "log", "-1", "--format=%cI", "--", str(args.site_dir)],
        text=True,
    ).strip()
    if not updated_at:
        raise ValueError("Could not find the latest website content change.")
    update_footers(args.site_dir, updated_at)
    # Quarto output and manually edited pages use the same stable public URLs.
    for page in args.site_dir.glob("*.html"):
        canonical = "https://www.daihongmin.com/" + ("" if page.name == "index.html" else page.name)
        content = page.read_bytes().decode("utf-8")
        tag = f'<link rel="canonical" href="{canonical}">'
        pattern = r'<link\b[^>]*rel="canonical"[^>]*>'
        if re.search(pattern, content):
            content = re.sub(pattern, tag, content)
        else:
            content = content.replace("</head>", tag + "\n</head>", 1)
        if page.name == "index.html":
            content = re.sub(r"<title>.*?</title>", "<title>Daihong Min (민대홍) | Economics Ph.D. Candidate, UC Davis</title>", content)
        # Shared palette and signature styles must follow page-specific rules.
        shared_styles = re.findall(r'<link\b[^>]*href="(?:\./)?(?:footer-layout|site-theme)\.css[^\"]*"[^>]*>', content)
        for style in shared_styles:
            content = re.sub(re.escape(style) + r'\s*', "", content)
        content = content.replace("</head>", "\n".join(shared_styles) + "\n</head>", 1)
        def fresh_asset(match):
            original = match.group(1)
            asset_name = original.split("?", 1)[0]
            asset = args.site_dir / asset_name
            if "/" in asset_name.removeprefix("./") or not asset.is_file():
                return match.group(0)
            version = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
            return f'"{asset_name}?v={version}"'
        content = re.sub(r'"((?:\./)?[^"/]+\.css(?:\?[^\"]*)?)"', fresh_asset, content)
        content = re.sub(r'"((?:\./)?site-events\.js(?:\?[^\"]*)?)"', fresh_asset, content)
        page.write_bytes(content.encode("utf-8"))

    cv_page = args.site_dir / "cv.html"
    cv_timestamp = subprocess.check_output(
        ["git", "log", "-1", "--format=%cI", "--", str(args.site_dir / "cv.pdf")],
        text=True,
    ).strip()
    if cv_timestamp:
        cv_updated = datetime.fromisoformat(cv_timestamp).astimezone(ZoneInfo("America/Los_Angeles"))
        content = cv_page.read_bytes().decode("utf-8")
        date_tag = f'<time data-cv-updated datetime="{cv_updated:%Y-%m}">{cv_updated:%B %Y}</time>'
        content, count = re.subn(r'<time\b[^>]*data-cv-updated[^>]*>.*?</time>', date_tag, content)
        if count != 1:
            raise ValueError("Expected one CV document update date.")
        cv_page.write_bytes(content.encode("utf-8"))
        print(f"CV PDF updated {cv_updated:%B %Y}")


if __name__ == "__main__":
    main()
