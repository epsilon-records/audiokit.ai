"""Markdown to HTML conversion utilities."""

import re
from pathlib import Path
from unicodedata import normalize

import markdown2

from audiokit_mcp_server.core.logger import logger


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    # Normalize unicode characters
    text = normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    # Convert to lowercase and replace spaces with hyphens
    text = re.sub(r"[^\w\s-]", "", text.lower())
    # Replace whitespace with single hyphen
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text


def ensure_artists_dir():
    """Ensure the artists directory exists."""
    artists_dir = Path("static/artists")
    artists_dir.mkdir(parents=True, exist_ok=True)
    return artists_dir


def save_artist_report(artist_id: str, artist_name: str, markdown_content: str) -> str:
    """Convert markdown to HTML and save to static directory."""
    try:
        artists_dir = ensure_artists_dir()

        # Create slug from artist name
        slug = slugify(artist_name)

        # Save markdown file
        md_path = artists_dir / f"{slug}.md"
        with open(md_path, "w") as f:
            f.write(markdown_content)
        logger.info(f"✍️ Saved markdown report to {md_path}")

        # Convert markdown to HTML
        html_content = markdown2.markdown(
            markdown_content,
            extras=[
                "fenced-code-blocks",
                "tables",
                "break-on-newline",
                "header-ids",
            ],
        )

        # Add some basic styling
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Artist Analysis: {artist_name}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container my-5">
                {html_content}
            </div>
        </body>
        </html>
        """

        # Save HTML file
        html_path = artists_dir / f"{slug}.html"
        with open(html_path, "w") as f:
            f.write(styled_html)

        logger.info(f"✍️ Saved HTML report to {html_path}")
        return f"/artists/{slug}.html"

    except Exception as e:
        logger.error(f"Failed to save artist report: {e!s}")
        raise
