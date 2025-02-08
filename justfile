#!/usr/bin/env sh

# AI Development Assistant Workflow
default:
    #!/usr/bin/env sh
    just --list

# Commit root project changes
commit:
    #!/usr/bin/env sh
    git add . && git commit -m "chore(ai): 🤖⚡️ Automated code alchemy in progress" || echo "⚠️ No changes in root project"

# Sync changes with the remote repository
sync:
    #!/usr/bin/env sh
    # Get current branch name
    BRANCH=$(git branch --show-current)
    # Pull changes before pushing
    git pull --rebase origin "$BRANCH"
    # Push changes to the remote
    git push origin "$BRANCH"
    echo "🌐 Changes synchronized with the remote repository"

# Check status of the repository
status:
    #!/usr/bin/env sh
    git status
    echo "🔍 Repository status checked"

# Add, commit, and push in one command
acp: commit sync
    #!/usr/bin/env sh
    echo "🚀 Changes added, committed, and pushed!"
    echo "436f646520617363656e64656421" | xxd -r -p

# Run all tests across all packages
test:
    pytest

# Run tests with coverage
test-cov:
    pytest --cov=packages/audiokit_ai/audiokit_ai --cov-report=term-missing

# Run tests in watch mode for development
test-watch:
    pytest-watch

# Run specific test file
test-file FILE:
    pytest {{FILE}} -v

# Generate requirements.txt
requirements:
    #!/usr/bin/env sh
    uv pip compile pyproject.toml --output-file requirements.txt

# Install dependencies from requirements.txt
install:
    #!/usr/bin/env sh
    uv pip install --editable ".[dev]"