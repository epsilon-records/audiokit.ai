#!/usr/bin/env sh

# AI Development Assistant Workflow
default:
    #!/usr/bin/env sh
    just --list

# Commit changes in both root and packages/audiokit
commit MESSAGE="":
    #!/usr/bin/env sh
    # Generate random AI-themed commit message
    MESSAGES=(
        "chore(ai): 🤖⚡️ Automated code alchemy in progress"
        "chore(ai): 🧠✨ Neural network optimization complete"
        "chore(ai): 🚀🌌 Launching code into the AI stratosphere"
        "chore(ai): 🧬🔮 Evolving code with genetic algorithms"
        "chore(ai): 🤖🎨 AI-generated code masterpiece"
        "chore(ai): 🧠💡 Neural network enlightenment achieved"
        "chore(ai): 🤖🌠 Code ascension to the AI heavens"
        "chore(ai): 🚀🤖 AI-powered code propulsion engaged"
        "chore(ai): 🧠⚙️ Cognitive code optimization complete"
        "chore(ai): 🤖🎯 Precision AI code targeting"
    )
    
    # Select random message if none provided
    if [ -z "$MESSAGE" ]; then
        MESSAGE=${MESSAGES[$RANDOM % ${#MESSAGES[@]}]}
    fi
    
    # Commit changes in packages/audiokit
    cd packages/audiokit && \
    git add . && \
    git commit -m "$MESSAGE" || echo "⚠️ No changes in packages/audiokit"
    # Return to root and commit changes
    cd ../.. && \
    git add . && \
    git commit -m "$MESSAGE" || echo "⚠️ No changes in root project"

# Sync changes in both root and packages/audiokit
sync:
    #!/usr/bin/env sh
    # Function to sync a repository
    sync_repo() {
        local path=$1
        cd "$path" || return
        BRANCH=$(git branch --show-current)
        if ! git ls-remote --heads origin "$BRANCH" | grep -q "$BRANCH"; then
            echo "🌱 Branch $BRANCH doesn't exist on remote. Creating..."
            git push --set-upstream origin "$BRANCH"
        fi
        git fetch origin && \
        git pull --rebase origin "$BRANCH" && \
        git push origin "$BRANCH" || echo "⚠️ No changes to sync in $path"
    }

    # Sync submodule
    sync_repo "packages/audiokit"
    
    # Sync root
    sync_repo "."
    
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