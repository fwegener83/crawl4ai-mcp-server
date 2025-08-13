# Finalize Feature Command

## Purpose
Run this when a feature branch is completed and ready to merge (e.g., during Pull Request finalization).  
Finalizes ADRs, updates the changelog, and commits the changes.

## Steps

1. **Identify Feature Context**
   - Detect current branch name (feature/{SUFFIX})
   - Retrieve related pull request description, commits, and linked issues
   - Load all ADR files in `docs/adr/` with status "Proposed" for this SUFFIX

2. **Finalize ADRs**
   - For each *Proposed* ADR related to this feature:
     - If the decision was implemented → set `Status: Accepted`
     - If the decision was discarded → set `Status: Rejected`
     - Add `Decision Date: YYYY-MM-DD`
     - Append a short “Implementation Outcome” section describing real-world result
   - If new architectural decisions were made during execution and not documented:
     - Create a new ADR file in `docs/adr/ADR_{date}_{short-title}.md` with status "Accepted"
   - Ensure all ADRs have unique IDs and proper filenames

3. **Generate Changelog Entry**
   - Edit `changelog.md`, adding an entry under **Unreleased**:
     - Categories: Added, Changed, Fixed, Deprecated
     - Include "Architecture Decisions" section listing:
       - Short decision summaries
       - Links to the ADR markdown files
   - Preserve markdown style and existing entries

4. **Commit Changes**
   - Stage updated `docs/adr/` and `changelog.md`
   - Commit with message:
     ```
     chore: finalize feature {SUFFIX}

     - Changelog entry added
     - ADRs finalized for this feature
     ```
   - Do NOT push automatically (leave to user/CI)

5. **Output Summary**
   - List all finalized ADRs with links
   - Show generated changelog entry
