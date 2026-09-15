# Local Git History Cleanup Plan

## 1. Why GitHub Rejected the Push
GitHub has a strict file size limit of 100 MB per file. The local history contains two large datasets that exceed this limit:
- `data/ground_truth/final/real_ground_truth_events.csv` (~228 MB)
- `data/ground_truth/events_real_expanded/real_events.csv` (~153 MB)
Because these files are part of the local Git commits, pushing the branch attempts to upload these oversized files to GitHub, resulting in a rejection.

## 2. Commits Containing the Large Files
The files were introduced and modified in the following commits (which are ahead of `origin/main`):
- `3258fa9` (model refined)
- `ef7bcd5` (HEAD -> main) (validation module refined)

`origin/main` is currently at `a627fac`.

## 3. Files to be Removed from Git History
The following files exceed 100 MB and must be removed from the Git history:
- `data/ground_truth/final/real_ground_truth_events.csv`
- `data/ground_truth/events_real_expanded/real_events.csv`

## 4. Confirmation of Local File Preservation
The files are present on the local filesystem and have been verified:
- `data/ground_truth/events_real_expanded/real_events.csv` (153.7 MB, modified 2026-09-14)
- `data/ground_truth/final/real_ground_truth_events.csv` (228.3 MB, modified 2026-09-14)

Furthermore, we verified that `.gitignore` successfully includes rules to ignore these specific paths, preventing them from being accidentally re-added.

## 5. Safest Local History-Cleanup Approach
The safest way to remove these files from the commit history without deleting them from the local filesystem or using destructive commands like `git filter-repo` is to perform a **Mixed Reset**:

1. Run `git reset origin/main` (which defaults to `--mixed`). 
   - This moves the `main` branch pointer back to `a627fac` (matching `origin/main`).
   - It **keeps all local filesystem modifications intact**.
   - It unstages all the changes from the two commits.
2. Run `git status` to verify that the large files are now untracked/ignored.
3. Because the `.gitignore` has been updated to include these files, running `git add .` will stage all the valid source code changes but will **ignore** the large datasets.
4. Run `git commit -m "Refined model and validation modules"` to group all the valid changes into a new, clean commit.

## 6. Rollback / Safety Considerations
- A **Mixed Reset** does not delete any files from the disk; it only alters Git's tracking and staging areas.
- Before doing anything, you could optionally copy the two large CSV files to a location outside the repository (e.g., `C:\Users\NIrmit\Desktop\Backup`) as a fail-safe.
- Since we are not doing any remote operations or rebasing pushed commits, there is no risk of messing up the remote repository state.
- **Do not use `git reset --hard`**, as that would permanently delete uncommitted changes and discard the files.
- **Do not use `git clean`**, as that might delete untracked files.
