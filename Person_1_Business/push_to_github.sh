#!/bin/bash
# ============================================================
# VinhaGuard AI — Push Person_1_Business contributions to GitHub
# Run this script from YOUR OWN terminal (not inside Claude).
#
# Usage:
#   cd ~/Desktop/ADV\ ML
#   bash Person_1_Business/push_to_github.sh
# ============================================================

set -e

REPO_URL="https://github.com/Schm1tzk4t3r/Advanced_ML"
BRANCH="person1-business"
TOKEN_PLACEHOLDER="YOUR_GITHUB_PAT_HERE"  # <-- replace or use git credential store

echo "=== VinhaGuard AI — GitHub Push Script ==="
echo ""

# 1. Clone repo if not already cloned
if [ ! -d ".git" ]; then
  echo "Cloning repository..."
  git clone "$REPO_URL" .
else
  echo "Already inside a git repo — pulling latest main..."
  git fetch origin
  git checkout main
  git pull origin main
fi

# 2. Create and switch to contribution branch
if git show-ref --quiet refs/heads/$BRANCH; then
  git checkout $BRANCH
  git merge main --no-edit
else
  git checkout -b $BRANCH
fi

echo "On branch: $(git branch --show-current)"

# 3. Copy contribution files (already in the folder alongside this script)
echo ""
echo "Files to commit:"
ls -lh "$(dirname "$0")"

# 4. Stage the Person_1_Business folder
git add Person_1_Business/

# 5. Commit
git config user.name  "Patrick Ansbach"
git config user.email "pabansbach@gmail.com"

git commit -m "feat(person1): add business & insurance lead contribution

- business_report.md: full business analysis (problem, market, product concept,
  unit economics, go-to-market, fairness/basis risk) with in-text citations
- unit_economics.ipynb: parametric premium formula, sensitivity analysis,
  portfolio revenue model, basis risk simulation
- README_business_section.md: folder overview for the main project README

Role: Person 1 — Business & Insurance Lead
Project: VinhaGuard AI — parametric climate insurance for Douro Valley wine producers
Course: Advanced Machine Learning, Nova SBE 2026" || echo "Nothing new to commit."

# 6. Push
echo ""
echo "Pushing to origin/$BRANCH ..."
git push origin $BRANCH

echo ""
echo "=== Done! ==="
echo "Next step: open a Pull Request on GitHub:"
echo "  $REPO_URL/compare/$BRANCH"
