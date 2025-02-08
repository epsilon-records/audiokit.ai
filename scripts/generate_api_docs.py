#!/usr/bin/env python3
"""
API Documentation Generator

This script:
1. Scans Python modules for docstrings
2. Generates API reference documentation using mkdocstrings
3. Creates example usage documentation
4. Updates the mkdocs navigation
"""

import os
import sys
import logging
import importlib
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("api_docs.log"), logging.StreamHandler()],
)


class APIDocGenerator:
    def __init__(self, src_dir: str, docs_dir: str):
        self.src_dir = Path(src_dir)
        self.docs_dir = Path(docs_dir)
        self.api_docs_dir = self.docs_dir / "api"
        self.examples_dir = self.docs_dir / "examples"

    def generate_module_doc(self, module_path: Path, relative_to: Path) -> str:
        """Generate documentation for a single module."""
        module_rel_path = module_path.relative_to(relative_to)
        module_name = str(module_rel_path).replace("/", ".").replace(".py", "")

        try:
            spec = importlib.util.spec_from_file_location(module_name, str(module_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            doc_content = f"# {module_name}\n\n"
            doc_content += f"## Module Documentation\n\n::: {module_name}\n\n"

            # Add examples if they exist
            example_path = self.examples_dir / f"{module_name}_example.py"
            if example_path.exists():
                doc_content += "## Examples\n\n"
                doc_content += "```python\n"
                doc_content += example_path.read_text()
                doc_content += "\n```\n"

            return doc_content

        except Exception as e:
            logging.error(f"Failed to generate docs for {module_name}: {str(e)}")
            return ""

    def create_example(self, module_path: Path, relative_to: Path) -> None:
        """Create an example file for a module."""
        module_rel_path = module_path.relative_to(relative_to)
        module_name = str(module_rel_path).replace("/", ".").replace(".py", "")

        try:
            spec = importlib.util.spec_from_file_location(module_name, str(module_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            example_content = f"""# Example usage of {module_name}

import {module_name}

def main():
    # Add example code here
    pass

if __name__ == "__main__":
    main()
"""

            example_path = self.examples_dir / f"{module_name}_example.py"
            example_path.parent.mkdir(parents=True, exist_ok=True)
            example_path.write_text(example_content)
            logging.info(f"Created example for {module_name}")

        except Exception as e:
            logging.error(f"Failed to create example for {module_name}: {str(e)}")

    def generate_all_docs(self) -> None:
        """Generate documentation for all Python modules."""
        # Create necessary directories
        self.api_docs_dir.mkdir(parents=True, exist_ok=True)
        self.examples_dir.mkdir(parents=True, exist_ok=True)

        # Find all Python files
        python_files = list(self.src_dir.rglob("*.py"))

        # Generate docs for each module
        for py_file in python_files:
            if py_file.name.startswith("_"):
                continue

            # Generate API docs
            doc_content = self.generate_module_doc(py_file, self.src_dir)
            if doc_content:
                rel_path = py_file.relative_to(self.src_dir)
                doc_path = self.api_docs_dir / rel_path.with_suffix(".md")
                doc_path.parent.mkdir(parents=True, exist_ok=True)
                doc_path.write_text(doc_content)
                logging.info(f"Generated docs for {rel_path}")

            # Create example
            self.create_example(py_file, self.src_dir)


def main():
    try:
        # Configure paths
        src_dir = os.path.join(os.getcwd(), "src")
        docs_dir = os.path.join(os.getcwd(), "docs")

        # Generate documentation
        generator = APIDocGenerator(src_dir, docs_dir)
        generator.generate_all_docs()

        logging.info("API documentation generation complete!")
        print("\nAPI documentation has been generated. Please:")
        print("1. Review the generated documentation")
        print("2. Update the examples with actual usage code")
        print("3. Build the documentation to verify")

    except Exception as e:
        logging.error(f"Documentation generation failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
