#!/usr/bin/env python3
"""Documentation testing script.

This script runs various documentation tests including:
- Markdown linting
- Link validation
- Code example testing
- Documentation coverage checks
- API documentation validation
- Comment style checking
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List

import yaml
from markdown_it import MarkdownIt
from openapi_spec_validator import validate_spec
from pydantic import BaseModel, Field
from pytest_cov.embed import cleanup_on_sigterm

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class TestResult(BaseModel):
    """Test result model."""

    name: str
    passed: bool
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class DocumentationTester:
    """Main documentation testing class."""

    def __init__(self, config_path: str):
        """Initialize with config file path."""
        self.config = self._load_config(config_path)
        self.results: List[TestResult] = []

    def _load_config(self, path: str) -> dict:
        """Load configuration from YAML file."""
        with open(path) as f:
            return yaml.safe_load(f)

    async def run_all_tests(self) -> bool:
        """Run all documentation tests."""
        try:
            # Run tests in parallel where possible
            await asyncio.gather(
                self.check_markdown(),
                self.validate_links(),
                self.test_code_examples(),
                self.check_coverage(),
                self.validate_api_docs(),
                self.check_comments(),
                self.verify_organization(),
            )

            # Generate report
            self._generate_report()

            # Return overall success
            return all(result.passed for result in self.results)

        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return False

    async def check_markdown(self):
        """Check markdown files for style and formatting."""
        logger.info("Checking markdown files...")

        try:
            md = MarkdownIt("commonmark")
            rules = self.config["markdown"]

            for md_file in Path(".").rglob("*.md"):
                content = md_file.read_text()

                # Check line length
                if rules["line_length"]:
                    long_lines = [
                        i + 1
                        for i, line in enumerate(content.splitlines())
                        if len(line) > rules["line_length"]
                    ]
                    if long_lines:
                        self.results.append(
                            TestResult(
                                name=f"Line length check: {md_file}",
                                passed=False,
                                errors=[
                                    f"Lines exceeding {rules['line_length']} chars: {long_lines}"
                                ],
                            )
                        )
                        continue

                # Parse and validate structure
                tokens = md.parse(content)
                headers = [t for t in tokens if t.type == "heading"]

                if rules["first_header_h1"] and (not headers or headers[0].tag != "h1"):
                    self.results.append(
                        TestResult(
                            name=f"First header check: {md_file}",
                            passed=False,
                            errors=["First header must be H1"],
                        )
                    )
                    continue

                self.results.append(
                    TestResult(name=f"Markdown check: {md_file}", passed=True)
                )

        except Exception as e:
            logger.error(f"Error checking markdown: {e}")
            self.results.append(
                TestResult(name="Markdown check", passed=False, errors=[str(e)])
            )

    async def validate_links(self):
        """Validate all documentation links."""
        logger.info("Validating links...")

        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                for md_file in Path(".").rglob("*.md"):
                    content = md_file.read_text()
                    links = self._extract_links(content)

                    for link in links:
                        if any(
                            p in link for p in self.config["links"]["ignore_patterns"]
                        ):
                            continue

                        try:
                            async with session.get(link) as response:
                                if response.status >= 400:
                                    self.results.append(
                                        TestResult(
                                            name=f"Link check: {link}",
                                            passed=False,
                                            errors=[f"Broken link: {response.status}"],
                                        )
                                    )
                                    continue
                        except Exception as e:
                            self.results.append(
                                TestResult(
                                    name=f"Link check: {link}",
                                    passed=False,
                                    errors=[str(e)],
                                )
                            )
                            continue

                    self.results.append(
                        TestResult(name=f"Link check: {md_file}", passed=True)
                    )

        except Exception as e:
            logger.error(f"Error validating links: {e}")
            self.results.append(
                TestResult(name="Link validation", passed=False, errors=[str(e)])
            )

    async def test_code_examples(self):
        """Test code examples in documentation."""
        logger.info("Testing code examples...")

        try:
            import pytest
            import jest

            # Test Python examples
            if self.config["code_examples"]["python"]["enabled"]:
                pytest_args = [
                    "--doctest-modules",
                    "--doctest-glob=*.md",
                    "--ignore="
                    + ",".join(
                        self.config["code_examples"]["python"]["ignore_patterns"]
                    ),
                ]
                result = pytest.main(pytest_args)
                self.results.append(
                    TestResult(name="Python examples", passed=result == 0)
                )

            # Test TypeScript examples
            if self.config["code_examples"]["typescript"]["enabled"]:
                jest_config = {
                    "roots": ["<rootDir>/docs"],
                    "testMatch": ["**/*.md"],
                    "transform": {"^.+\\.tsx?$": "ts-jest"},
                }
                result = jest.runCLI(jest_config, ["."])
                self.results.append(
                    TestResult(name="TypeScript examples", passed=result.success)
                )

        except Exception as e:
            logger.error(f"Error testing code examples: {e}")
            self.results.append(
                TestResult(name="Code examples", passed=False, errors=[str(e)])
            )

    async def check_coverage(self):
        """Check documentation coverage."""
        logger.info("Checking documentation coverage...")

        try:
            from coverage import Coverage

            cov = Coverage(
                source=["audiokit"], omit=self.config["coverage"]["ignore_patterns"]
            )

            # Measure docstring coverage
            if self.config["coverage"]["check_docstrings"]:
                cov.start()
                cov.stop()

                total = cov.report()
                if total < self.config["coverage"]["minimum_coverage"]:
                    self.results.append(
                        TestResult(
                            name="Documentation coverage",
                            passed=False,
                            errors=[
                                f"Coverage {total}% below minimum {self.config['coverage']['minimum_coverage']}%"
                            ],
                        )
                    )
                else:
                    self.results.append(
                        TestResult(name="Documentation coverage", passed=True)
                    )

        except Exception as e:
            logger.error(f"Error checking coverage: {e}")
            self.results.append(
                TestResult(name="Coverage check", passed=False, errors=[str(e)])
            )

    async def validate_api_docs(self):
        """Validate API documentation."""
        logger.info("Validating API documentation...")

        try:
            # Validate OpenAPI spec
            if self.config["api_docs"]["validate_openapi"]:
                with open("openapi.json") as f:
                    spec = yaml.safe_load(f)
                    validate_spec(spec)

            # Check required sections
            api_docs = Path("docs/api")
            for doc in api_docs.rglob("*.md"):
                content = doc.read_text()
                missing_sections = []

                for section in self.config["api_docs"]["required_sections"]:
                    if section.lower() not in content.lower():
                        missing_sections.append(section)

                if missing_sections:
                    self.results.append(
                        TestResult(
                            name=f"API doc sections: {doc}",
                            passed=False,
                            errors=[f"Missing sections: {missing_sections}"],
                        )
                    )
                else:
                    self.results.append(
                        TestResult(name=f"API doc sections: {doc}", passed=True)
                    )

        except Exception as e:
            logger.error(f"Error validating API docs: {e}")
            self.results.append(
                TestResult(name="API documentation", passed=False, errors=[str(e)])
            )

    async def check_comments(self):
        """Check code comments style."""
        logger.info("Checking comment style...")

        try:
            import pylint.lint
            import eslint

            # Check Python comments
            python_rc = {
                "docstring-convention": self.config["comments"]["python"]["style"],
                "required-docstring-sections": self.config["comments"]["python"][
                    "required_sections"
                ],
            }

            pylint_args = ["--rcfile=" + str(Path("pylintrc").absolute()), "audiokit"]
            pylint.lint.Run(pylint_args)

            # Check TypeScript comments
            eslint_config = {
                "rules": {
                    "jsdoc/require-jsdoc": [
                        "error",
                        {
                            "require": {
                                "FunctionDeclaration": True,
                                "MethodDefinition": True,
                                "ClassDeclaration": True,
                            }
                        },
                    ],
                    "jsdoc/require-param": "error",
                    "jsdoc/require-returns": "error",
                }
            }

            result = eslint.lintFiles(["src/**/*.ts"], eslint_config)
            if result.errorCount > 0:
                self.results.append(
                    TestResult(
                        name="TypeScript comments",
                        passed=False,
                        errors=[str(result.errorCount) + " style errors found"],
                    )
                )
            else:
                self.results.append(TestResult(name="TypeScript comments", passed=True))

        except Exception as e:
            logger.error(f"Error checking comments: {e}")
            self.results.append(
                TestResult(name="Comment style", passed=False, errors=[str(e)])
            )

    async def verify_organization(self):
        """Verify documentation organization."""
        logger.info("Verifying documentation organization...")

        try:
            # Check required files
            missing_files = []
            for required_file in self.config["organization"]["required_files"]:
                if not Path(required_file).exists():
                    missing_files.append(required_file)

            if missing_files:
                self.results.append(
                    TestResult(
                        name="Required files",
                        passed=False,
                        errors=[f"Missing files: {missing_files}"],
                    )
                )
            else:
                self.results.append(TestResult(name="Required files", passed=True))

            # Check required sections
            for doc_type, sections in self.config["organization"][
                "required_sections"
            ].items():
                if doc_type == "readme":
                    content = Path("README.md").read_text()
                elif doc_type == "api_docs":
                    content = Path("docs/api/README.md").read_text()

                missing_sections = []
                for section in sections:
                    if section.lower() not in content.lower():
                        missing_sections.append(section)

                if missing_sections:
                    self.results.append(
                        TestResult(
                            name=f"{doc_type} sections",
                            passed=False,
                            errors=[f"Missing sections: {missing_sections}"],
                        )
                    )
                else:
                    self.results.append(
                        TestResult(name=f"{doc_type} sections", passed=True)
                    )

        except Exception as e:
            logger.error(f"Error verifying organization: {e}")
            self.results.append(
                TestResult(
                    name="Documentation organization", passed=False, errors=[str(e)]
                )
            )

    def _generate_report(self):
        """Generate test report."""
        logger.info("Generating test report...")

        try:
            import junit_xml

            test_cases = []
            for result in self.results:
                case = junit_xml.TestCase(result.name)

                if not result.passed:
                    case.add_failure_info(
                        message="\n".join(result.errors),
                        output="\n".join(result.warnings),
                    )

                test_cases.append(case)

            test_suite = junit_xml.TestSuite("Documentation Tests", test_cases)
            with open(self.config["output"]["report_file"], "w") as f:
                junit_xml.TestSuite.to_file(f, [test_suite], prettyprint=True)

        except Exception as e:
            logger.error(f"Error generating report: {e}")

    def _extract_links(self, content: str) -> List[str]:
        """Extract links from markdown content."""
        import re

        # Match markdown and HTML links
        markdown_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        html_links = re.findall(r'<a[^>]+href=["\'](.*?)["\']', content)

        return [link[1] for link in markdown_links] + html_links


def main():
    """Main entry point."""
    config_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "docs/testing/documentation_test_config.yml"
    )

    tester = DocumentationTester(config_path)
    success = asyncio.run(tester.run_all_tests())

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    cleanup_on_sigterm()
    main()
