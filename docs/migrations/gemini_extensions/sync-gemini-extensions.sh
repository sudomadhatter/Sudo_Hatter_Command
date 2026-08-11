#!/bin/bash
# sync-gemini-extensions.sh
# Syncs Gemini/Antigravity extensions (plugins & skills) between the local machine and this git repo.

ACTION=$1
# The script lives IN gemini_extensions/, so its own directory IS the repo dir.
# It used to append "/gemini_extensions" onto that, producing a path one level too
# deep: import then found no plugins/ or skills/, copied nothing, and still printed
# "Done." A silent success on the fresh-machine path (SCC-89).
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_DIR="$HOME/.gemini/config"

if [ "$ACTION" == "export" ]; then
    echo "Exporting extensions from $LOCAL_DIR to $REPO_DIR..."
    mkdir -p "$REPO_DIR"
    if [ -d "$LOCAL_DIR/plugins" ]; then
        cp -R "$LOCAL_DIR/plugins" "$REPO_DIR/"
        echo "Exported plugins."
    fi
    if [ -d "$LOCAL_DIR/skills" ]; then
        cp -R "$LOCAL_DIR/skills" "$REPO_DIR/"
        echo "Exported skills."
    fi
    echo "Done. You can now commit the changes in $REPO_DIR."
elif [ "$ACTION" == "import" ]; then
    echo "Importing extensions from $REPO_DIR to $LOCAL_DIR..."
    mkdir -p "$LOCAL_DIR"
    if [ -d "$REPO_DIR/plugins" ]; then
        cp -R "$REPO_DIR/plugins" "$LOCAL_DIR/"
        echo "Imported plugins."
    fi
    if [ -d "$REPO_DIR/skills" ]; then
        cp -R "$REPO_DIR/skills" "$LOCAL_DIR/"
        echo "Imported skills."
    fi
    echo "Done. Restart your Gemini/Antigravity instance to load the extensions."
else
    echo "Usage: ./sync-gemini-extensions.sh [export|import]"
    echo "  export - Copies extensions from your local ~/.gemini/config to the git repo"
    echo "  import - Copies extensions from the git repo to your local ~/.gemini/config"
    exit 1
fi
