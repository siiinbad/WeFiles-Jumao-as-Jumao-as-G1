# GitHub workflow - preparation only

The account baseline and every existing branch are retained. main and develop
were preserved by the local feature reorganization. The current public origin
is https://github.com/siiinbad/WeFiles-Jumao-as-Jumao-as-G1.
The local setup fix is prepared separately on feature/local-setup.

## Separate feature branches and commits

| Feature | Branch | Feature commit |
| --- | --- | --- |
| Private vault CRUD and ownership | feature/private-file-vault | c87ac0f |
| Render deployment preparation | feature/render-deployment | 3ef0f48 |
| File and folder search | feature/vault-search | 22e04f5 |
| WeFiles UI and role dashboard summaries | feature/wefiles-ui | c5e2b6a |
| PD2 implementation documentation and draft report | feature/pd2-documentation | See this branch's latest commit |
| Fresh-clone local setup | feature/local-setup | c46e2e0 and its documentation follow-up |

The new branches are created from develop and fast-forwarded to their required
feature dependency before committing their own feature. The dependency order is:
private-file-vault -> render-deployment -> vault-search -> wefiles-ui ->
pd2-documentation -> local-setup. Each branch has its own feature commit; upstream commits are
shared prerequisites. No dependency was merged into develop or main locally.

feature/reference-ui is preserved at fc78926 as the original combined UI
checkpoint. Its content has been separated into the active search, UI and
documentation branches above. Keep this checkpoint; use the separated branches
for future PRs rather than submitting the old combined branch again.

## Required remote workflow

1. Reconcile with the same existing repository and retain its history. The
   reference ../WeFiles/ checkout uses https://github.com/siiinbad/WeFiles and
   has an independent history. Do not force-push this checkout over it.
2. Confirm the required public name WeFiles-Lastname-Firstname-Section, protect
   main/develop and disable automatic deletion of merged feature branches.
3. Push each active feature branch. Open a separate PR into develop for each
   feature, in dependency order, and run its checks before merging. Keep branches.
   After merging a prerequisite, verify that the next PR shows only its feature.
4. When the increment is accepted, open develop -> main, run checks and merge.
   This release remains pending while the increment is intentionally unfinished.
5. Record actual merged PR links in the report. The minimum remains two merged
   feature PRs into develop and one merged develop-to-main PR. Local branch refs
   and commits do not replace real merged GitHub PRs.

## Submission evidence still needed

- Same public repository with the required final name and preserved history.
- Merged feature and release PR URLs; keep all feature branches.
- Live Supabase database/private storage and hosted Render acceptance.
- Final student/section details, labeled screenshots and working test accounts.
- Signed final docs/WeFiles-Lastname-Firstname-Section-PD2.pdf and its commit.

## Recorded GitHub history

Existing merged PRs were verified during setup work: file search in PR #1,
WeFiles UI in PR #2, and PD2 documentation in PR #3. Each currently targets main.
A remote develop branch was not present when checked. Record this actual history
in the draft; the requested feature -> develop -> main workflow still needs to
be established for subsequent increments. The setup fix stays on its own
feature/local-setup branch and does not merge or move main/develop.
