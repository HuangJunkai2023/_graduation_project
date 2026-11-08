# Issue tracker: GitHub

Repository: `HuangJunkai2023/_graduation_project`.
Issues and specifications live in GitHub Issues. Use `gh` from this repository
or pass `--repo HuangJunkai2023/_graduation_project` explicitly.

## Operations

- Read: `gh issue view NUMBER --json number,title,body,labels,comments`.
- List: `gh issue list --state open --json number,title,labels`.
- Create: `gh issue create --title "TITLE" --body-file /path/to/body.md`.
- Update: `gh issue edit NUMBER --body-file /path/to/body.md`.
- Comment: `gh issue comment NUMBER --body-file /path/to/comment.md`.
- Label: `gh issue edit NUMBER --add-label LABEL` (or `--remove-label LABEL`).
- Close: `gh issue close NUMBER` after its acceptance criteria are met.

Write multiline bodies to UTF-8 files, preserving actual newlines.
When a skill says to publish to the issue tracker, create a GitHub issue;
when it says to fetch a ticket, read the referenced issue and its comments.
Use one issue per implementation ticket. Record parent and blocking links;
where native links are unavailable, use `Part of #NUMBER` and
`Blocked by: #NUMBER` in the body. Work only when all blockers are resolved.

**PRs as a request surface: no.**

## Access status

On 2026-11-08, local `gh` returned HTTP 401 (Bad credentials) for repository
metadata and label queries. Remote access, Issues availability and label
creation remain unverified. Authenticate with `gh auth login --hostname github.com`
and repeat those checks before remote writes. Keep credentials out of tickets.
An authentication failure does not change the selected tracker or prove that
an issue or label was created. Update this status after successful verification.
