"""Fill the supplied template without removing sections; generate an unsigned draft PDF.

Install requirements-docs.txt, then run python scripts/generate_pd2_draft.py.
Final identity, screenshots, real test accounts and PR evidence require manual completion.
"""
from pathlib import Path
import re
from xml.sax.saxutils import escape

from docx import Document
from docx.table import Table as DocxTable
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


def fill_table(table, rows):
    while len(table.rows) < len(rows):
        table.add_row()
    for row, values in zip(table.rows, rows):
        for cell, value in zip(row.cells, values):
            cell.text = value


def main():
    document = Document(DOCS / "PD-Completion-Report-Template.docx")
    replacements = {
        "[System description]": "WeFiles gives members a private place to organize and retrieve files. Administrators manage records across member accounts. This increment extends the existing Django account feature using the separate WeFiles application as a reference.",
        "[Name of core feature, e.g., Appointment Booking]": "Private file vault: folders, uploads, downloads and record management",
        "[Justification]": "Organizing and retrieving files is the main purpose of WeFiles. This vertical slice connects account identity, role permissions, PostgreSQL records and private file storage through the UI.",
        "[Feature Name]": "Private File Vault",
        "[What the feature does, in 2\u20133 sentences.]": "Members create nested folders, upload and download files, edit metadata or locations, and confirm deletion of their own records. Admins manage records across owners. PostgreSQL persistence is verified locally; live Supabase PostgreSQL and private S3 bucket acceptance remain pending.",
        "[Step 1, e.g., Customer logs in and opens Products]": "1. Register/sign in as a Member and open My files from the member dashboard.",
        "[Step 2]": "2. Create a folder/subfolder, upload a file, open its details and download it.",
        "[Step 3]": "3. Edit its name/description/location; confirm deletion, then delete empty folders. Admin uses All files for cross-account management.",
        "[Screenshot 1 \u2013 caption]": "Pending screenshot 1: member dashboard, nested folders, upload and file detail/download. Capture from the running app after Supabase setup; do not present mockups as evidence.",
        "[Screenshot 2 \u2013 caption]": "Pending screenshot 2: validation error, edit/delete confirmation and Admin All files. Local Chrome desktop/mobile, theme, keyboard and core-flow acceptance passed; final hosted screenshots remain pending.",
        "[Firstname Lastname]": "Pending student name - unsigned draft",
        "[MM/DD/YYYY]": "Pending submission date (draft prepared 11/18/2026)",
    }
    for paragraph in document.paragraphs:
        value = paragraph.text
        if value.startswith("How to use this template:"):
            paragraph.text = "DRAFT - NOT FOR SUBMISSION. Prepared 11/18/2026. Every template section is retained. Supabase, GitHub merges, screenshots, working test accounts and student details remain pending."
            continue
        for old, new in replacements.items():
            value = value.replace(old, new)
        if value != paragraph.text:
            paragraph.text = value
    tables = document.tables
    fill_table(tables[0], [
        ["System Name", "WeFiles"],
        ["Student Name", "Pending confirmed Lastname, Firstname"],
        ["Section", "Pending confirmed section"],
        ["Increment", "Project Development 2 - Core Feature (Vertical Slice), in progress"],
        ["GitHub Repository", "Public repository: https://github.com/siiinbad/WeFiles-Jumao-as-Jumao-as-G1. Confirm final student/section naming before submission."],
        ["Date Submitted", "Not submitted; draft prepared 11/18/2026"],
    ])
    fill_table(tables[1], [
        ["Feature", "Status", "Notes"],
        ["Account Registration", "Partial", "Implemented; local PostgreSQL registration, uniqueness and password tests pass. Hosted Supabase/browser acceptance pending."],
        ["Login / Logout", "Partial", "Session login and POST logout pass local tests; hosted acceptance pending."],
        ["Role-Based User Dashboard", "Partial", "Admin/Member redirects, direct URL restrictions and scoped file counts pass local tests; hosted acceptance pending."],
        ["User Profile (view and edit)", "Partial", "Own contact fields persist locally; role/identity changes are rejected. Hosted acceptance pending."],
    ])
    fill_table(tables[2], [["Role", "What this role can do in the feature"],
        ["Member", "Create/read/update/delete own files and folders; private downloads; own dashboard and profile."],
        ["Admin", "View/update/delete files and folders across members; own uploads/new folders; account statistics. Original owners remain unchanged."],
    ])
    fill_table(tables[3], [
        ["Operation", "Implemented? (Yes/No)", "Where in the UI", "Who can do it"],
        ["Create", "Yes - local tests", "My files > New folder / Upload a file", "Signed-in Member/Admin; creator owns record"],
        ["Read", "Yes - local tests", "My files / All files > folder / file details / Download file", "Owner; Admin across owners"],
        ["Update", "Yes - local tests", "Edit folder / Edit details (name, description, location)", "Owner; Admin across owners"],
        ["Delete", "Yes - local tests", "Delete > confirmation; folders must be empty", "Owner; Admin across owners"],
    ])
    fill_table(tables[4], [
        ["Model / Table", "Key Fields", "Relationships (ForeignKey / ManyToMany)"],
        ["Folder / vault_folder", "UUID, owner, parent, name, created_at, updated_at", "owner -> accounts.User; optional parent -> Folder"],
        ["VaultFile / vault_vaultfile", "UUID, owner, folder, blob key, name, description, size_bytes, content_type, timestamps", "owner -> accounts.User; optional folder -> Folder"],
        ["StorageDeletionJob / vault_storagedeletionjob", "storage_key, attempts, next_attempt_at, last_error_code", "Independent deletion outbox after a VaultFile row is removed"],
        ["User / accounts_user", "username, email, password hash, role; Django identity fields", "One user owns many files/folders; standard auth groups/permissions M2M retained"],
    ])
    fill_table(tables[5], [
        ["Layer", "File path(s)"],
        ["Models", "accounts/models.py; vault/models.py; accounts/migrations/; vault/migrations/"],
        ["Views", "accounts/views.py; vault/views.py; vault/services.py"],
        ["URLs", "config/urls.py; accounts/urls.py; vault/urls.py"],
        ["Forms", "accounts/forms.py; vault/forms.py"],
        ["Templates", "templates/accounts/*.html; vault/templates/vault/*.html; templates/base.html"],
        ["Deployment / storage", "config/environment.py; vault/storage.py; build.sh; start.sh; render.yaml; .env.example"],
    ])
    fill_table(tables[6], [
        ["Rule", "How it is enforced"],
        ["Required fields and valid formats", "Django forms validate registration, profile, names and descriptions; errors appear beside inputs."],
        ["Upload must contain 1 byte to 50 MiB; names cannot contain paths/control characters", "UploadForm, model validation and upload service; random storage keys; errors/success messages."],
        ["Member can manage only own records", "Login-protected URLs; scoped queries; owner FKs; service checks and destination selectors. Admin is the explicit cross-owner role."],
        ["Folder uniqueness, same-owner parents and valid tree", "Case-insensitive DB constraints; form/model/service checks; serialized owner mutations; max depth 12 including moved subtree."],
        ["Deletion requires confirmation; folders must be empty", "POST confirmation, CSRF, protected FKs, empty-folder check; durable retry jobs for object cleanup."],
        ["Hosted uploads require private durable storage", "Production settings require private Supabase S3 configuration; no public URL generation; authorized attachment downloads."],
    ])
    fill_table(tables[7], [
        ["Branch", "Merged Into", "Pull Request Link", "What it contains"],
        ["feature/private-file-vault", "Pending -> develop", "Pending - no remote PR created", "Owner-linked vault CRUD, account integration, validation, private storage and PostgreSQL tests"],
        ["feature/render-deployment", "Pending -> develop", "Pending - no remote PR created", "Render build/start/health setup, CI, environment guide and draft report"],
        ["feature/vault-search", "main (existing history)", "https://github.com/siiinbad/WeFiles-Jumao-as-Jumao-as-G1/pull/1", "Owner-scoped file/folder search form, queries and search regression tests; commit 22e04f5"],
        ["feature/wefiles-ui", "main (existing history)", "https://github.com/siiinbad/WeFiles-Jumao-as-Jumao-as-G1/pull/2", "WeFiles branding, themes, screens and role dashboard summaries; commit c5e2b6a"],
        ["feature/pd2-documentation", "main (existing history)", "https://github.com/siiinbad/WeFiles-Jumao-as-Jumao-as-G1/pull/3", "Implementation notes, verification, feature branch evidence and the draft report"],
        ["feature/local-setup", "Pending -> develop", "Pending - no remote PR created", "Fresh-clone .env generation, persistent PostgreSQL Compose service, cross-platform instructions and isolated-clone verification"],
        ["feature/reference-ui", "Preserved checkpoint", "Not a separate active PR", "Original combined UI checkpoint retained; active work is split into search, UI and documentation branches"],
        ["develop", "Pending -> main", "Pending - intentionally not released", "Required integration/release flow pending; recorded PRs 1-3 target main and remote develop was absent when checked"],
    ])
    fill_table(tables[8], [
        ["No.", "Task", "Description", "Priority", "Target Increment"],
        ["1", "Configure Supabase", "New PostgreSQL app project, private storage bucket/S3 credentials, protected Data API exposure; apply migrations.", "High", "PD2 before release"],
        ["2", "Hosted acceptance", "Run browser flow, owner/role checks, persistence across restart, real storage error/retry checks; verify approved ERD.", "High", "PD2 before release"],
        ["3", "GitHub workflow", "Reconcile same repository/history, required public name; merge 2 feature PRs into develop and 1 develop PR into main; retain branches.", "High", "PD2 before submission"],
        ["4", "Report evidence", "Add student/section, labeled screenshots and working role test accounts; sign declaration and save with required final PDF name.", "High", "PD2 before submission"],
        ["5", "Render deployment", "Set environment, deploy only when authorized/ready, verify HTTPS, health, static assets and storage persistence.", "High", "PD2 when ready"],
    ])
    fill_table(tables[9], [
        ["Issue ID", "Description", "Steps to Reproduce", "Severity", "Status / Workaround"],
        ["ISS-01", "Supabase environment is not set up; hosted persistence/storage not verified.", "Start production without database/S3 environment values.", "Critical", "Open - configure cloud resources; local PostgreSQL tests pass."],
        ["ISS-02", "Final repository naming, merged PR evidence and Render URL need confirmation in this draft.", "Review the public origin and the branch/PR records; verify hosted deployment when ready.", "Major", "Open - confirm student/section naming and record actual merged PR/deployment links."],
        ["ISS-03", "Final hosted screenshots and identity/test-account information pending.", "Review Screenshots, Project Information and Test Accounts sections.", "Major", "Open - keep report unsigned and clearly marked draft."],
        ["ISS-04", "Existing source database/legacy Supabase SQL cannot be reused directly.", "Compare increment User/migrations with reference WeFiles schema.", "Major", "Use a new increment DB; plan a migration separately if preserving old user data."],
    ])
    fill_table(tables[10], [
        ["Role", "Username / Email", "Password"],
        ["Admin", "Pending - create a real demo account after Supabase setup, then promote via management command", "Pending dedicated test password; no personal credentials"],
        ["Member", "Pending - create Member A and Member B to demonstrate ownership isolation", "Pending dedicated test password; no personal credentials"],
    ])
    for section in document.sections:
        section.header.paragraphs[0].text = "WeFiles PD2 | DRAFT - NOT FOR SUBMISSION"
    document.core_properties.title = "WeFiles PD2 Implementation / Completion Report - Draft"
    document.core_properties.subject = "In-progress implementation; not a completed submission"
    document.save(DOCS / "WeFiles-PD2-DRAFT.docx")
    # Preserve the template order and every section in a readable PDF export.
    styles = getSampleStyleSheet()
    body = ParagraphStyle("ReportBody", parent=styles["BodyText"], fontSize=9, leading=12, spaceAfter=7)
    cell_style = ParagraphStyle("ReportCell", parent=body, fontSize=7.5, leading=10, spaceAfter=0)
    heading = ParagraphStyle("ReportHeading", parent=styles["Heading2"], textColor=colors.HexColor("#214d3b"), spaceBefore=14)
    story = []
    def clean(text):
        return text.translate(str.maketrans({0x2013: "-", 0x2014: "-", 0x2192: "->", 0x2019: "'", 0x201c: '\"', 0x201d: '\"', 0xa0: " "}))
    def p(text, style=body):
        return Paragraph(escape(clean(text)).replace("\n", "<br/>"), style)
    for item in document.iter_inner_content():
        if isinstance(item, DocxTable):
            rows = [[p(cell.text, cell_style) for cell in row.cells] for row in item.rows]
            count = len(rows[0])
            widths = {2: [135, 375], 3: [122, 105, 283], 4: [85, 96, 183, 146], 5: [40, 100, 205, 60, 105]}[count]
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e7efe9")),
                ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#b9c8bf")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.extend([table, Spacer(1, 10)])
        elif item.text.strip():
            text = item.text.strip()
            is_heading = bool(re.match(r"^([1-6]\.|2\.[12])", text)) or text in {"Project Information", "User Roles and Access", "User Flow", "CRUD Operations", "Database Models", "Key Files", "Validation and Business Rules", "Branches and Pull Requests", "Screenshots"}
            story.append(p(text, heading if is_heading else body))
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#69796e"))
        canvas.drawString(42, 25, "DRAFT - NOT FOR SUBMISSION | Supabase, PRs and final evidence pending")
        canvas.drawRightString(A4[0] - 42, 25, str(doc.page))
        canvas.restoreState()
    SimpleDocTemplate(str(DOCS / "WeFiles-PD2-DRAFT.pdf"), pagesize=A4,
                      rightMargin=42, leftMargin=42, topMargin=38, bottomMargin=42,
                      title="WeFiles PD2 - Draft", author="WeFiles").build(story, onFirstPage=footer, onLaterPages=footer)
    expected = ["1. Project Overview", "2. Features Implemented in This Increment", "3. Remaining Tasks", "4. Outstanding Issues", "5. Test Accounts", "6. Declaration"]
    text = "\n".join(p.text for p in document.paragraphs)
    assert "[" not in text, "Unfilled template paragraph"
    assert all(section in text for section in expected), "A required template section is missing"
    assert not any("[" in cell.text for table in document.tables for row in table.rows for cell in row.cells), "Unfilled template cell"
    print("Saved docs/WeFiles-PD2-DRAFT.docx and docs/WeFiles-PD2-DRAFT.pdf; all required sections retained.")


if __name__ == "__main__":
    main()
