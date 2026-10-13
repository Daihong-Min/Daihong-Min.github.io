"""Render the published CV into browser-independent preview pages."""

import argparse
import hashlib
from pathlib import Path
import re
import subprocess
import tempfile


def render_preview(site_dir: Path) -> int:
    pdf = site_dir / "cv.pdf"
    page = site_dir / "cv.html"
    content = page.read_text(encoding="utf-8")
    container = r'<div class="cv-preview-pages"[^>]*>.*?</div>'
    if len(re.findall(container, content, re.DOTALL)) != 1:
        raise ValueError("Expected one CV preview container.")
    version = hashlib.sha256(pdf.read_bytes()).hexdigest()[:12]
    output_dir = site_dir / "cv-preview"
    output_dir.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cv-preview-") as temporary:
        prefix = Path(temporary) / "page"
        subprocess.run(
            ["pdftoppm", "-jpeg", "-jpegopt", "quality=85", "-scale-to", "1600",
             str(pdf), str(prefix)],
            check=True,
        )
        images = sorted(Path(temporary).glob("page-*.jpg"),
                        key=lambda p: int(p.stem.split("-")[-1]))
        if not images:
            raise ValueError("No CV preview pages were rendered.")
        markup = ['<div class="cv-preview-pages" aria-label="CV page previews">']
        for number, image in enumerate(images, start=1):
            name = f"{version}-page-{number}.jpg"
            (output_dir / name).write_bytes(image.read_bytes())
            loading = "eager" if number == 1 else "lazy"
            markup.append(
                f'<a href="cv.pdf#page={number}" target="_blank" rel="noopener noreferrer">'
                f'<img src="cv-preview/{name}" alt="CV page {number} of {len(images)}; open PDF" '
                f'loading="{loading}" decoding="async"></a>'
            )
        markup.append("</div>")
    content = re.sub(container, "\n".join(markup), content, flags=re.DOTALL)
    page.write_text(content, encoding="utf-8")
    print(f"Rendered {len(images)} CV preview pages ({version}).")
    return len(images)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, default=Path("docs"))
    render_preview(parser.parse_args().site_dir)
