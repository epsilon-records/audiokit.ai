import shutil
from pathlib import Path


def create_structure(base_path: Path):
    """Create the new directory structure"""
    directories = [
        base_path / "apps/web",
        base_path / "packages/audiokit/audiokit",
        base_path / "packages/audiokit/tests",
        base_path / "scripts",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "__init__.py").touch()


def move_files(base_path: Path):
    """Move files to their new locations"""
    # Move SvelteKit files
    sveltekit_files = [
        "package.json",
        "tsconfig.json",
        "svelte.config.js",
        "vite.config.ts",
        ".gitignore",
        "src",
        "static",
    ]

    for item in sveltekit_files:
        src = base_path / item
        if src.exists():
            dest = base_path / "apps/web" / item
            shutil.move(str(src), str(dest))

    # Move Python files
    python_files = {
        "audiokit.py": "packages/audiokit/audiokit/core.py",
        "config.yaml": "packages/audiokit/config.yaml",
    }

    for src_file, dest_file in python_files.items():
        src = base_path / src_file
        if src.exists():
            dest = base_path / dest_file
            shutil.move(str(src), str(dest))


def split_python_code(base_path: Path):
    """Split the Python code into separate modules"""
    core_path = base_path / "packages/audiokit/audiokit/core.py"
    logger_path = base_path / "packages/audiokit/audiokit/logger.py"
    llm_path = base_path / "packages/audiokit/audiokit/llm.py"
    utils_path = base_path / "packages/audiokit/audiokit/utils.py"

    # Read the original file
    with open(core_path, "r") as f:
        lines = f.readlines()

    # Split into sections
    logger_code = []
    llm_code = []
    utils_code = []
    core_code = []

    current_section = core_code
    for line in lines:
        if "class Logger:" in line:
            current_section = logger_code
        elif "class LLMRequest:" in line:
            current_section = llm_code
        elif "def sanitize_artist_data" in line:
            current_section = utils_code

        current_section.append(line)

    # Write the split files
    with open(logger_path, "w") as f:
        f.writelines(logger_code)

    with open(llm_path, "w") as f:
        f.writelines(llm_code)

    with open(utils_path, "w") as f:
        f.writelines(utils_code)

    with open(core_path, "w") as f:
        f.writelines(core_code)


def main():
    base_path = Path(__file__).parent.parent
    create_structure(base_path)
    move_files(base_path)
    split_python_code(base_path)
    print("Restructuring complete!")


if __name__ == "__main__":
    main()
