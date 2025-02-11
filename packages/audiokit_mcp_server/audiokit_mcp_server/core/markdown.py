"""Markdown to HTML conversion utilities."""

from pathlib import Path

import markdown2

from audiokit_mcp_server.core.logger import logger


def ensure_artists_dir():
    """Ensure the artists directory exists."""
    artists_dir = Path("static/artists")
    artists_dir.mkdir(parents=True, exist_ok=True)
    return artists_dir


def save_artist_report(artist_id: str, markdown_content: str) -> str:
    """Convert markdown to HTML and save to static directory."""
    try:
        artists_dir = ensure_artists_dir()

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
            <title>Artist Analysis: {artist_id}</title>
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
        file_path = artists_dir / f"{artist_id}.html"
        with open(file_path, "w") as f:
            f.write(styled_html)

        logger.info(f"✍️ Saved artist report to {file_path}")
        return f"/artists/{artist_id}.html"

    except Exception as e:
        logger.error(f"Failed to save artist report: {e!s}")
        raise
