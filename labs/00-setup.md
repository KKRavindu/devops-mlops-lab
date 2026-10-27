# Lab 00: Setup & Git Workflow

**Goal:** Get the repo under version control on GitHub and learn the branch → PR → merge
flow that every later lab uses.

## Theory
- **Everything as code.** In DevOps, Git is the single source of truth: app code,
  infrastructure, pipelines, config, and (in MLOps) the *parameters* and *pointers to data*
  that produced a model.
- **Trunk-based development.** Short-lived feature branches, small PRs, merge to `main`
  often. CI runs on every PR, and `main` is always deployable.
- **Conventional commits** (`feat:`, `fix:`, `ci:`, `docs:`) make history readable and
  enable automated changelogs.

## Tasks
1. Initialise and push:
   ```bash
   cd ~/Projects/devops-mlops-lab
   git init -b main
   git add . && git commit -m "chore: initial lab platform"
   # create an EMPTY repo on github.com named devops-mlops-lab, then:
   git remote add origin git@github.com:<you>/devops-mlops-lab.git
   git push -u origin main
   ```
2. Set up the Python environment:
   ```bash
   make setup
   source .venv/bin/activate
   ```
3. Practise the PR flow:
   ```bash
   git switch -c docs/my-notes
   mkdir notes && echo "# My lab notes" > notes/README.md
   git add notes && git commit -m "docs: start lab notes"
   git push -u origin docs/my-notes
   ```
   Open the PR on GitHub, review the diff, merge it, then `git switch main && git pull`.
4. Protect `main`: in GitHub, go to Settings → Branches → add a rule requiring a PR
   (and later, passing status checks).

## Checkpoint
- `git log --oneline` shows your commits, and GitHub shows the merged PR.
- `make help` lists all commands.

## Break it
- Make conflicting edits to the same line on two branches and resolve the merge conflict.
- Commit a fake secret (`API_KEY=abc123`) on a branch, then remove it from history with
  `git reset` before pushing. Discuss why "delete it in the next commit" isn't enough.

## Interview questions
- Merge vs rebase: when do you use each?
- What is trunk-based development and why does it pair well with CI/CD?
- How would you remove a secret that was already pushed? (Rotate it first.)
