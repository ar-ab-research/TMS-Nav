# Positional comparison delivery report

## Latest delivery

- Supplied planned-target text export now imports automatically through the subject CLI. Legacy `NIfTI:Scanner` support is gated on validated scanner qform/sform metadata, with raw positions/orientations and full source provenance preserved.
- Automatically maps named SMA variants to internal SMA and F4/right-DLPFC names to right_DLPFC; keeps unmatched names unassigned and missing sites absent. Does not infer cap-marker identities or invent a replacement target.
- Extracts and caches scalp from the supplied Brainsight anatomical MRI. Renders imported raw targets on that source-native anatomy beside the existing cap anatomy, with separate frame captions. Display translation is only layout and never used for measurements.
- Right sidebar shows imported target names/site assignments and rendered count. Source target labels, raw-target toggle, cap projection controls, reload and exports remain functional. Source positions also appear in CSV with explicit source-frame fields.
- Different-MRI primary distances remain blocked until verified registration and reviewed marker/scalp semantics are available. No scalp-contact meaning is inferred from the name “Skin”.

## Verification

- Actual local CLI regenerated JSON/CSV and source scalp successfully.
- Actual Chrome browser acceptance passed: both imported target labels visible, source scalp loaded, sidebar rendered-count equals imported target count; toggles, reload and JSON export passed without browser exceptions.
- Positional suite: 10 passed, including autonomous site-name mapping and gated legacy scanner support. Full Python suite: **90 passed**.
- Production viewer build passed; private generated outputs and browser screenshot remain ignored locally.
- Local API/viewer started for inspection on ports 8765/1234 without regenerating or staging the user's dataset registry.

## Remaining

- Primary cross-MRI distances require verified registration and cap-marker/scalp-point semantics; missing planned target cannot yield a comparison.
- Anatomical/registration accuracy and independent-export validation remain unvalidated.
- Unrelated staged datasetRegistry.js edit preserved and excluded from delivery.
- Prior automatic-review rejection of external push remains unresolved; no push retry/bypass attempted.
