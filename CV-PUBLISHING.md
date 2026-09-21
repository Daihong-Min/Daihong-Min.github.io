# Publishing the CV from Overleaf

The CV is edited in the existing Overleaf project:
https://www.overleaf.com/project/680077d7e505a4fb1bc0e02a

After editing `main.tex`, recompile and review the PDF. Open **Integrations → GitHub → Push Overleaf changes to GitHub** and confirm the push. Editing or recompiling alone does not publish the CV.

## Automatic steps after pushing

1. The private `Daihong-Min/CV` repository receives the approved `main.tex`.
2. Its **Publish CV to website** workflow copies that file to this repository's `cv.tex` and pushes a commit using a repository-specific SSH deploy key.
3. **Build CV** compiles the source and commits identical PDFs to `cv.pdf` and `docs/cv.pdf`.
4. On successful completion, **Deploy website** publishes `docs/` to GitHub Pages. This explicit step also handles PDF commits made with `GITHUB_TOKEN`, which do not trigger another push workflow.

The published URL remains https://www.daihongmin.com/cv.pdf. Homepage download links and the CV page preview use this same file. The prose in `cv.qmd` is maintained separately.

## Status and recovery

- Source delivery: https://github.com/Daihong-Min/CV/actions
- PDF build and deployment: https://github.com/Daihong-Min/Daihong-Min.github.io/actions
- A failed LaTeX build leaves the previously published PDF in place. Fix the source in Overleaf and push again.
- For a transient delivery or deployment error, rerun the failed workflow from Actions.
- Do not routinely edit `cv.tex` in this repository; Overleaf is the editing source. Changes made directly to `cv.tex` must also be incorporated in Overleaf before the next publication.
- The current CV is a single self-contained `main.tex`. If it later needs images, bibliography files, or custom style files, extend the delivery workflow to transfer those dependencies before publishing.

## Connection maintenance

The secret `WEBSITE_CV_DEPLOY_KEY` is stored in the private CV repository. The matching public deploy key on this website repository grants access only to this repository. It is used to push `cv.tex`; no Overleaf token or account-wide GitHub token is required.

The Pages publishing source is **GitHub Actions**. General website updates still publish from the existing `docs/` directory.
