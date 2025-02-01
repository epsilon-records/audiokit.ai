#!/usr/bin/env python3
"""Documentation build and deployment script.

This script handles:
- Documentation generation
- Version management
- Search index creation
- Asset optimization
- Deployment to hosting
"""

import argparse
import logging
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

import yaml
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class DocBuilder:
    """Documentation builder class."""

    def __init__(self, config_path: str = "mkdocs.yml"):
        """Initialize with MkDocs config path."""
        self.config_path = config_path
        self.config = self._load_config()
        self.docs_dir = Path("docs")
        self.site_dir = Path("site")

    def _load_config(self) -> dict:
        """Load MkDocs configuration."""
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def build(self, version: Optional[str] = None) -> bool:
        """Build documentation."""
        try:
            logger.info("Building documentation...")

            # Prepare assets
            self._prepare_assets()

            # Build docs
            cmd = ["mkdocs", "build", "--clean"]
            if version:
                cmd.extend(["--site-dir", f"site/{version}"])

            result = subprocess.run(cmd, check=True)

            # Post-process
            self._post_process()

            return result.returncode == 0

        except Exception as e:
            logger.error(f"Error building docs: {e}")
            return False

    def serve(self, port: int = 8000) -> None:
        """Serve documentation locally."""
        try:
            logger.info(f"Serving documentation on port {port}...")
            subprocess.run(["mkdocs", "serve", "-a", f"localhost:{port}"], check=True)
        except Exception as e:
            logger.error(f"Error serving docs: {e}")

    def deploy(self, version: str) -> bool:
        """Deploy documentation."""
        try:
            logger.info(f"Deploying version {version}...")

            # Build for version
            if not self.build(version):
                return False

            # Deploy using mike
            subprocess.run(["mike", "deploy", version], check=True)

            return True

        except Exception as e:
            logger.error(f"Error deploying docs: {e}")
            return False

    def _prepare_assets(self):
        """Prepare documentation assets."""
        logger.info("Preparing assets...")

        assets_dir = self.docs_dir / "assets"
        assets_dir.mkdir(exist_ok=True)

        # Optimize images
        for img_path in assets_dir.glob("*.{png,jpg,jpeg}"):
            try:
                img = Image.open(img_path)
                img.save(img_path, optimize=True, quality=85)
            except Exception as e:
                logger.warning(f"Error optimizing {img_path}: {e}")

        # Copy static files
        static_dir = Path("static")
        if static_dir.exists():
            shutil.copytree(static_dir, assets_dir / "static", dirs_exist_ok=True)

    def _post_process(self):
        """Post-process generated documentation."""
        logger.info("Post-processing documentation...")

        # Create search index
        self._create_search_index()

        # Generate sitemap
        self._generate_sitemap()

        # Add version selector
        self._add_version_selector()

    def _create_search_index(self):
        """Create search index."""
        try:
            subprocess.run(["mkdocs-lunr-indexer"], check=True)
        except Exception as e:
            logger.warning(f"Error creating search index: {e}")

    def _generate_sitemap(self):
        """Generate sitemap."""
        try:
            subprocess.run(["mkdocs-sitemap"], check=True)
        except Exception as e:
            logger.warning(f"Error generating sitemap: {e}")

    def _add_version_selector(self):
        """Add version selector to docs."""
        try:
            versions = self._get_versions()
            if not versions:
                return

            # Add version selector to each HTML file
            for html_file in self.site_dir.rglob("*.html"):
                self._inject_version_selector(html_file, versions)

        except Exception as e:
            logger.warning(f"Error adding version selector: {e}")

    def _get_versions(self) -> List[str]:
        """Get list of documentation versions."""
        try:
            result = subprocess.run(
                ["mike", "list"], capture_output=True, text=True, check=True
            )
            return [
                line.split()[0] for line in result.stdout.splitlines() if line.strip()
            ]
        except Exception as e:
            logger.warning(f"Error getting versions: {e}")
            return []

    def _inject_version_selector(self, html_file: Path, versions: List[str]):
        """Inject version selector into HTML file."""
        content = html_file.read_text()

        # Create version selector HTML
        selector = """
        <div class="md-version-select">
            <label>Version:</label>
            <select onchange="window.location.href=this.value">
        """

        for version in versions:
            selector += f'<option value="/{version}/">{version}</option>'

        selector += """
            </select>
        </div>
        """

        # Insert before closing body tag
        content = content.replace("</body>", f"{selector}</body>")

        html_file.write_text(content)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build and deploy documentation")
    parser.add_argument("--version", help="Documentation version")
    parser.add_argument(
        "--serve", action="store_true", help="Serve documentation locally"
    )
    parser.add_argument("--deploy", action="store_true", help="Deploy documentation")
    parser.add_argument("--port", type=int, default=8000, help="Port for local server")

    args = parser.parse_args()
    builder = DocBuilder()

    if args.serve:
        builder.serve(args.port)
    elif args.deploy:
        if not args.version:
            parser.error("Version required for deployment")
        success = builder.deploy(args.version)
        exit(0 if success else 1)
    else:
        success = builder.build(args.version)
        exit(0 if success else 1)


if __name__ == "__main__":
    main()
