---
name: Frozen scikit-learn artifact compatibility
description: Runtime compatibility note for the preserved DGA Sentinel joblib models.
---

The frozen joblib models were trained with scikit-learn 1.6.1 and emit
`InconsistentVersionWarning` when loaded by the available scikit-learn 1.9.1
runtime, but the complete regression suite and live inference succeeded.

**Why:** The models are frozen source-of-truth artifacts; retraining or
re-serializing them just to remove a warning would change the deployment
contract.

**How to apply:** Treat the warning as expected unless inference or regression
outputs fail. Preserve the original model files and authoritative ensemble
configuration.