# Phase 16E-R2 Unknown & Confidence Audit

## 1. Metric Definitions & Reconciled Results
- **UNKNOWN_RATE**: 0.0390 (`78` predicted UNKNOWN / `2000` total events)
- **TRUE_UNKNOWN_COUNT**: 198
- **UNKNOWN_TO_INDUSTRIAL_FP**: 92 (true UNKNOWN events predicted as Industrial Fire)
- **UNKNOWN_TO_INDUSTRIAL_FPR**: 0.4646 (`92` FP / `198` true UNKNOWN events) — *Corrected Denominator*
- **UNNECESSARY_UNKNOWN**: 0.0000 (`0` events rejected despite defensible argmax and sufficient evidence)

## 2. Confidence Calibration Audit
- **HIGH_CONFIDENCE_FP**: 17
- **HIGH_CONFIDENCE_FN**: 4
- **HIGH_CONFIDENCE_WRONG_RATE**: 0.0117
- **LOW_EVIDENCE_KNOWN_RATE**: 0.7970
