#!/usr/bin/env sh

# AI Development Assistant Workflow
default:
    #!/usr/bin/env sh
    just --list

# Commit changes in both root and packages/audiokit
commit:
    #!/usr/bin/env sh
    # Commit changes in packages/audiokit
    cd packages/audiokit && \
    git add . && \
    git commit -m "chore(ai): 🤖⚡️ Automated code alchemy in progress" || echo "⚠️ No changes in packages/audiokit"
    # Return to root and commit changes
    cd ../.. && \
    git add . && \
    git commit -m "chore(ai): 🤖⚡️ Automated code alchemy in progress" || echo "⚠️ No changes in root project"

# Add a new command to clean up Git objects
clean:
    #!/usr/bin/env sh
    git prune
    rm -f .git/gc.log
    echo "🧹 Git repository cleaned"

# Sync changes in both root and packages/audiokit
sync:
    #!/usr/bin/env sh
    # Get current branch name
    BRANCH=$(git branch --show-current)
    
    # Clean up before sync
    just clean
    
    # Sync changes in packages/audiokit
    cd packages/audiokit && \
    git fetch origin && \
    git pull --rebase origin "$BRANCH" && \
    git push origin "$BRANCH" || echo "⚠️ No changes to sync in packages/audiokit"
    
    # Return to root and sync changes
    cd ../.. && \
    git fetch origin && \
    git pull --rebase origin "$BRANCH" && \
    git push origin "$BRANCH"
    echo "🌐 Changes synchronized with the remote repository"

# Check status of the repository
status:
    #!/usr/bin/env sh
    git status
    echo "🔍 Repository status checked"

# Update acp to include cleanup
acp: clean commit sync
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

# Install dependencies from requirements.txt
install:
    #!/usr/bin/env sh
    # Install core packages in development mode
    pip install -e packages/audiokit_ai
    pip install -e packages/audiokit
    
    # Generate requirements if needed
    if [ ! -f "requirements.txt" ]; then
        just requirements
    fi
    
    # Install any additional requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # Verify installation
    echo "Testing audiokit CLI..."
    ak --help

# Generate requirements.txt
requirements:
    #!/usr/bin/env sh
    echo "# Generated requirements for audiokit.ai" > requirements.txt
    echo "# Core dependencies" >> requirements.txt
    pip freeze | grep -v "audiokit" >> requirements.txt