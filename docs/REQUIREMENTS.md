# Increment 2 requirement status - in progress

## What was already present

The increment repository already contained committed account registration,
login/logout, role dashboards and profile editing. Its uncommitted private vault
implementation was preserved and extended. The separate `../WeFiles/` app
provided reference folder/upload/download/cleanup behavior; it has broader shared
workspace features and a different account schema. Chat, notifications, favorites,
email verification and membership approval are outside this selected increment.

## Requirement mapping

| Requirement | Implementation/evidence | Status |
| --- | --- | --- |
| End-to-end core UI | My files/All files - folder - upload - details/download - edit/move - confirmed delete | Implemented; local Chrome acceptance passed, hosted checks pending |
| Persistence | PostgreSQL ORM and migrations; private Supabase S3 bytes in production | Prepared; live Supabase pending |
| CRUD | vault/views.py, forms.py, services.py, templates | Implemented |
| Validation/messages | Required inputs, size/name/description limits, destination ownership, folder uniqueness/cycles/depth, empty-folder deletion | Implemented with tests |
| Logged-in owner-linked records | vault/urls.py login wrappers; owner FKs and scoped queries; immutable owner in services | Implemented |
| Roles/dashboards | Member own records; Admin all records; dashboard counts/links; controlled promotion | Implemented |
| Relationships | User - Folder/VaultFile; Folder - children/files; deletion outbox | Modeled; compare with approved external ERD before final |
| Registration | Validated username/email/password, member default | Preserved |
| Login/logout | Session auth, CSRF, POST logout, safe next redirect | Preserved |
| Role dashboard | Server role checks and redirects | Preserved |
| User profile | Session-user view/edit; no privilege or identity fields | Preserved |
| Render | Build/start/Blueprint/health, private storage settings, automatic deploys off | Prepared only |
| Secrets/dependencies/setup | .gitignore, .env.example, requirements.txt, README | Updated |
| Same public repository and required name | Public origin: siiinbad/WeFiles-Jumao-as-Jumao-as-G1 | Verify final student/section naming and PR evidence |
| Required branches/merged PRs | main/develop baseline; separate vault, deployment, search, UI and documentation feature commits; workflow document | Local preparation; 2 feature -> develop and 1 develop -> main merged PRs pending |
| Completion report PDF in docs | Original template retained; draft DOCX/PDF preserves all sections | Draft only; identity, screenshots, accounts, PRs and final filename pending |

## Relationships

- `accounts.User` has many `vault.Folder` rows through `Folder.owner`.
- `accounts.User` has many `vault.VaultFile` rows through `VaultFile.owner`.
- `Folder.parent` is an optional self ForeignKey; nonempty folders are protected.
- `VaultFile.folder` is an optional ForeignKey protected against folder deletion.
- `StorageDeletionJob` records pending cleanup keys independently after a file row
  is deleted. It is an outbox, not a second owner of the file.
- No core ManyToMany relationship is needed for a private vault. Django's standard
  authentication groups/permissions retain their own ManyToMany relationships.

Do not mark the increment complete until the hosted checks, real GitHub PR
workflow and final report evidence are recorded.

The UI is now adapted from the original WeFiles shell, account screens and vault
components. See UI_REFERENCE.md for provenance and local browser verification.

Fresh-clone startup is provided by scripts/configure_local.py, compose.yaml and
the platform-specific README commands on feature/local-setup. Verification from
an isolated clone passed 8 setup tests and 56 Django tests; see VERIFICATION.md.
