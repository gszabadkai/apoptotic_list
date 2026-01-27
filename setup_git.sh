#!/bin/bash
#
# setup_git.sh - Initialize Git Repository for Apoptotic Gene List Project
#
# Usage:
#   chmod +x setup_git.sh
#   ./setup_git.sh
#
# This script will:
#   1. Initialize a new git repository
#   2. Add all files (respecting .gitignore)
#   3. Create the first commit
#   4. Print instructions for adding a remote
#

set -e  # Exit on any error

echo "========================================"
echo "  Apoptotic Gene List - Git Setup"
echo "========================================"
echo ""

# Check if already a git repo
if [ -d ".git" ]; then
    echo "Warning: This directory is already a git repository."
    read -p "Do you want to continue and create a new commit? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
else
    echo "[1/4] Initializing git repository..."
    git init
    echo "      Done."
fi

echo ""
echo "[2/4] Staging files (respecting .gitignore)..."
git add .
echo "      Done. Staged files:"
git status --short | head -20
STAGED_COUNT=$(git status --short | wc -l)
if [ "$STAGED_COUNT" -gt 20 ]; then
    echo "      ... and $((STAGED_COUNT - 20)) more files"
fi

echo ""
echo "[3/4] Creating initial commit..."
git commit -m "Initial commit: Apoptotic gene list analysis

This repository contains a comprehensive analysis pipeline for assembling
apoptotic gene lists from multiple sources (GO, KEGG, Reactome, GSEA).

Contents:
- workflow/: Python scripts for data acquisition and processing
- results/: Final annotated gene list (1,232 genes)
- figures/: Category distribution visualization
- README.md: Full documentation

Generated with K-Dense (www.k-dense.ai)"

echo "      Done."

echo ""
echo "[4/4] Repository setup complete!"
echo ""
echo "========================================"
echo "  Next Steps"
echo "========================================"
echo ""
echo "To push this repository to GitHub:"
echo ""
echo "  1. Create a new repository on GitHub (https://github.com/new)"
echo "     - Do NOT initialize with README, .gitignore, or license"
echo ""
echo "  2. Add your GitHub repo as the remote:"
echo "     git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
echo ""
echo "  3. Push to GitHub:"
echo "     git branch -M main"
echo "     git push -u origin main"
echo ""
echo "========================================"
echo ""
