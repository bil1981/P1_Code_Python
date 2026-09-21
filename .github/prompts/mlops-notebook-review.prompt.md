
git add .
git commit -m "chore: initialize project"
git tag v0.1.0

git add .
git commit -m "feat: add prediction API"
git tag v0.2.0

git add .
git commit -m "test: add automated API tests"
git tag v0.3.0

git add .
git commit -m "ci: add CI pipeline"
git tag v0.4.0

git add .
git commit -m "build: containerize application"
git tag v0.5.0

git add .
git commit -m "feat: add monitoring report"
git tag v1.0.0


Puis envoyer les tags sur GitHub :

git push origin main
git push origin --tags


si erreur 
 Add-Content .gitignore "`n*.db"
 git reset --soft origin/main
Add-Content .gitignore "`n*.db"
Add-Content .gitignore "`ncredit_risk.db"
 Add-Content .gitignore "`nhome_credit.db"
 git rm --cached credit_risk.db home_credit.db -f
                fatal: pathspec 'credit_risk.db' did not match any files
 git add .
 git commit -m "feat: mise a jour complete du projet sans les bases .db"
# Remplacer le tag local par le nouveau commit
git tag -f v0.1.2
# Pousser la branche main
git push origin main
# Pousser également les tags sur GitHub
git push origin --tags
 git tag -d v0.1.0

 git tag -d v0.1.1
> git tag -d v0.1.2
 git tag v0.1.2
 git push origin v0.1.2

---
mode: agent
description: "Review, debug, and improve an ML notebook or script in this MLOps project with clear engineering and business-focused recommendations."
---

You are acting as a senior ML engineer and MLOps reviewer for this repository.

Review the current notebook or selected code in the context of this project and produce a practical, production-minded analysis.

Objectives:
1. Understand the business problem and the evaluation metric being optimized.
2. Check the ML workflow for correctness, hidden risks, and reproducibility issues.
3. Identify modeling, preprocessing, validation, and deployment concerns.
4. Suggest concrete, minimal improvements with code examples when needed.
5. Keep the answer actionable for a real-world data-science project, not only a classroom exercise.

Use the repository context when relevant, especially:
- tabular classification tasks and risk/business-cost tradeoffs
- cross-validation, train/test separation, and leakage risks
- feature engineering and preprocessing consistency
- model comparison, threshold tuning, and business metrics
- MLflow tracking, reproducibility, experiment logging, and deployment readiness

When reviewing the selected code or notebook section:
- explain what the code is doing in plain language
- point out likely bugs, data issues, or modeling mistakes
- assess whether the metric matches the business objective
- highlight any missing validation or monitoring steps
- recommend a cleaner or more robust implementation

Output format:
1. Quick summary of what the workflow is trying to achieve
2. Key findings (bugs, risks, or quality issues)
3. Recommended improvements with short code snippets if useful
4. Priority next steps for productionizing the pipeline
5. Optional: if the code is broken, propose a corrected version of the relevant block

Stay concise, technical, and practical. Prefer precise recommendations over generic advice.

Example invocations:
- /mlops-notebook-review
- /mlops-notebook-review on the selected model training cell
- /mlops-notebook-review on the current notebook section and tell me what is risky before deployment
