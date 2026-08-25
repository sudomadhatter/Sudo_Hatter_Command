---
name: firestore-update-splits-field-paths-on-dots
description: "Firestore update() parses a dotted STRING key as a field PATH, so any map key containing a dot (every Gemini model ID) writes to the wrong place and reports success."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 281bcbeb-e806-472f-ad38-c5bac3f66f3c
  modified: 2026-08-24T17:53:01.435Z
---

⛔ **`doc_ref.update({f"models.{key}": value})` is wrong whenever `key` contains a dot** — and every
Gemini model ID does (`gemini-3.7-flash`, `gemini-3.1-flash-lite`, `gemini-live-2.5-flash-native-audio`).

`update()` treats a dotted string as a **field path**, not a field name. So `"models.gemini-3.7-flash"`
is three segments, and the write lands at `models -> "gemini-3" -> "7-flash"`.

**Why it is dangerous rather than merely wrong:** Firestore returns success, sibling keys are
untouched, and the doc still looks healthy. Only a read-back at the intended key reveals it.

Measured 2026-08-24 on AGY production `dashboard_metadata/pricing_config` (story 19.5): the write
created `models["gemini-3"]["7-flash"]`, and `cost_meter._compute_cost` kept metering
`gemini-3.7-flash` at **$0.00** — the exact condition the write existed to fix. Caught only because
the script asserted a read-back. Story 11.9 had hit the same trap ("dotted-key maps never nested").

**The correct form** — escape each segment:

```python
from google.cloud.firestore_v1.field_path import FieldPath
path = FieldPath("models", model).to_api_repr()   # -> models.`gemini-3.7-flash`
ref.update({path: rates})
```

**How to apply:** never build a Firestore field path by f-string. Use `FieldPath(...).to_api_repr()`
whenever any segment is data rather than a literal you typed. **Always read back the intended key
after the write** — this class of corruption is invisible to the write's own return value. When
cleaning up a bad write, assert the bogus node's exact shape before deleting it.

Related: [[destructive-reverify-must-read-fresh]] (a cached re-check no-ops and looks green) and
the AGY seeder that now encodes this, `backend/scripts/seed_pricing_config.py`.
