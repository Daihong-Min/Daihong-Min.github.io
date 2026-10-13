"""Stamp published footers with the month of the latest website content change."""

import argparse
from datetime import datetime
from pathlib import Path
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


if __name__ == "__main__":
    main()
