# Repository Large File Audit

## Background
A recent Git push was rejected by GitHub due to two files exceeding the 100 MB limit. This audit identifies those files, documents their tracking status, and outlines the correct repository hygiene procedures without deleting the local data or prematurely rewriting Git history.

## Identified Large Files

### 1. `data/ground_truth/final/real_ground_truth_events.csv`
- **Size**: 221.06 MB
- **Status**: Tracked (Committed in local `main`, causing the push rejection)
- **Classification**: Generated Output (Produced by `gold_decision_engine.py`)
- **Recommended Treatment**: Untrack from Git index (`git rm --cached`). Ignore via `.gitignore`.
- **Local Copy Preserved**: YES

### 2. `data/ground_truth/events_real_expanded/real_events.csv`
- **Size**: 146.59 MB
- **Status**: Tracked (Committed in local `main`, causing the push rejection)
- **Classification**: Generated Output (Produced by `reconstruct_real_events.py`)
- **Recommended Treatment**: Untrack from Git index (`git rm --cached`). Ignore via `.gitignore`.
- **Local Copy Preserved**: YES

### 3. Sentinel-2 TIFF Cache Files (Multiple)
- **Paths**: `data/interim/sentinel2/cache/*.tif` (e.g., `S2C_43RBQ_20260618_0_L2A_B04.tif`)
- **Size**: Varies (~50 MB to 250 MB each)
- **Status**: Untracked (Currently ignored by `data/interim/` rule in `.gitignore`)
- **Classification**: Generated/Downloaded Cache
- **Recommended Treatment**: Maintain current `.gitignore` rule.
- **Local Copy Preserved**: YES

### 4. `data/synthetic/simulated_expert_reviews.csv`
- **Size**: 89.87 MB
- **Status**: Tracked
- **Classification**: Generated Output / Source
- **Recommended Treatment**: Keep tracked (under 100 MB), but monitor if it grows in future phases.
- **Local Copy Preserved**: YES

## Executed Hygiene Actions
1. **No Data Loss**: All local files remain completely intact. No files were deleted.
2. **`.gitignore` Updated**: Explicit ignore rules were appended for `data/ground_truth/events_real_expanded/real_events.csv`, `data/ground_truth/final/real_ground_truth_events.csv`, and all raw FIRMS CSVs (`data/ground_truth/firms_real_expanded/*.csv`).
3. **Metadata Preserved**: Small canonical manifests (`canonical_observation_manifest.csv`, `acquisition_manifest.json`) were explicitly whitelisted (`!`) in `.gitignore` to ensure the reproducibility of the dataset.
4. **No Remote Operations**: No pushes or history rewrites were performed, in strict compliance with the local-only mandate.

## Next Steps for the User
To resolve the GitHub push rejection, the local Git history must be rewritten to remove these two files from the latest commit, since Git prevents pushing commits containing >100MB blobs. Because you explicitly requested **no Git history rewrite**, this has not been done yet.

When you are ready, you can resolve the branch state by running:
```bash
git reset HEAD~1
git rm --cached data/ground_truth/final/real_ground_truth_events.csv
git rm --cached data/ground_truth/events_real_expanded/real_events.csv
git commit -m "Update Phase16 ground truth metadata (excluding large generated csv)"
```
