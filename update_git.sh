#!/bin/bash
#
# update_git.sh - Update Existing Git Repository with Source Breakdown Files
#
# Usage:
#   chmod +x update_git.sh
#   ./update_git.sh
#
# This script will:
#   1. Verify you're in a git repository
#   2. Stage the new source breakdown files
#   3. Create a commit
#   4. Push to your remote repository
#
# Prerequisites:
#   - You must have already run setup_git.sh and pushed to GitHub
#   - Your remote should already be configured

set -e  # Exit on any error

echo "========================================"
echo "  Apoptotic Gene List - Repository Update"
echo "========================================"
echo ""

# Check if this is a git repo
if [ ! -d ".git" ]; then
    echo "ERROR: This directory is not a git repository."
    echo ""
    echo "If this is a fresh download, run setup_git.sh instead."
    echo "If you already have a repository elsewhere, copy these new files into it."
    exit 1
fi

# Check for remote
REMOTE=$(git remote -v 2>/dev/null | head -1)
if [ -z "$REMOTE" ]; then
    echo "WARNING: No remote configured."
    echo "After committing, you'll need to add a remote and push manually."
    echo ""
fi

echo "[1/3] Checking for new files..."
echo ""

# Show what will be staged
NEW_FILES=$(git status --porcelain | grep -E "^\?\?" | wc -l || true)
MODIFIED_FILES=$(git status --porcelain | grep -E "^ M|^M " | wc -l || true)

if [ "$NEW_FILES" -eq 0 ] && [ "$MODIFIED_FILES" -eq 0 ]; then
    echo "No new or modified files detected."
    echo "Your repository is already up to date!"
    exit 0
fi

echo "Found changes:"
git status --short
echo ""

echo "[2/3] Staging and committing changes..."
echo ""

# Stage all changes
git add .

# Create commit
git commit -m "Add source-specific breakdown lists

New files in results/source_breakdown/:
- apoptosis_genes_KEGG.csv (84 genes from KEGG Apoptosis pathway)
- apoptosis_genes_Reactome.csv (215 genes from Reactome pathways)
- apoptosis_genes_Hallmark.csv (161 genes from MSigDB Hallmark)
- apoptosis_genes_GO.csv (1,012 genes from GO Biological Process)
- breakdown_summary.txt (statistics)

Each file contains genes filtered by source, with consensus categories
(Pro-apoptotic, Anti-apoptotic, Ambiguous, Unspecified) preserved from
the consolidated analysis.

Updated README.md with Step 5 documentation.

Generated with K-Dense (www.k-dense.ai)"

echo ""
echo "[3/3] Pushing to remote..."
echo ""

# Try to push
if git remote -v | grep -q "origin"; then
    git push origin main 2>/dev/null || git push origin master 2>/dev/null || {
        echo ""
        echo "WARNING: Push failed. This might be because:"
        echo "  1. You need to authenticate (check your credentials)"
        echo "  2. The branch name is different (try: git push origin HEAD)"
        echo "  3. You need to pull first (try: git pull --rebase && git push)"
        echo ""
        echo "Your changes have been committed locally."
        echo "Try pushing manually: git push"
        exit 0
    }
    echo "Done! Changes pushed successfully."
else
    echo "No remote configured. Changes committed locally."
    echo ""
    echo "To push your changes:"
    echo "  1. Add remote: git remote add origin https://github.com/USERNAME/REPO.git"
    echo "  2. Push: git push -u origin main"
fi

echo ""
echo "========================================"
echo "  Update Complete!"
echo "========================================"
echo ""
echo "Your repository now includes the source-specific breakdown files."
echo ""
