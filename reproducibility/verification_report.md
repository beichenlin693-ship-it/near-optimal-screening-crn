# Reproducibility verification report

**PASS — publication repository build dated 2026-10-06.**

## Source and scope

The source was the approved SIMPAT submission-preparation archive dated
2026-10-04, SHA-256 `723ea53d180190dc82f1d88a0c9f37d20971e41ea994258a76e4529fd5f8abc7` (261,271,487 bytes),
plus the previously verified computational source and configuration artifacts
identified by hash in `source_artifacts.csv`. No source package was modified.
This repository is a selected lightweight release, not a raw project-tree dump.

## Contents

|Item|Count / status|
|---|---|
|Scientific result/display files|73|
|Machine-readable CSV files|47: 42 full-precision aggregate tables plus 5 exact display-row tables|
|Approved main tables|5 TeX artifacts|
|Approved main figures|7 figures × 3 formats (PNG/PDF/SVG)|
|Reproduction/verification scripts|5: 3 public entrypoints plus 2 plotting helpers|
|Library Python files|33, including package initializers|
|Selected scientific-source AST comparisons|27 PASS; imports, documentation and ROOT/VERSION assignments excluded from comparison|
|Source artifacts verified|98 unchanged at source; 69 included byte-identically|
|Derived input projection|1,578 forecast rows; selected strings exactly equal source columns; no refit|
|Main-display traceability chains|12, all referenced files present|
|Excluded archive/raw/intermediate entries|13; see excluded_artifacts.csv|

The counts distinguish files from independent experiments. Multiple display
formats, reused reference tables and rounded rows add no independent evidence.

## Completed checks

1. All 33 library files import in a fresh Python 3.14.4 environment installed
   using only `requirements.txt`; no simulator entrypoint is invoked. The direct
   pins reflect observed versions. The complete dependency closure actually
   installed for verification is in `clean_environment_lock.txt`.
2. The five tables reproduce byte-for-byte, preserving their original line
   endings and exact displayed precision. Tables 3–4 are also independently
   formatted from the underlying full-precision stored summaries.
3. All seven figures redraw with identical PNG pixels in that clean environment.
   PDF/SVG timestamps and internal metadata are not treated as numerical changes.
   The archived approved image/PDF/SVG artifacts themselves are byte-identical to
   the manuscript source artifacts.
4. Release verification passes 17 checks covering hashes, complete manifest
   coverage, source correspondence, file sizes, excluded archive types, local
   user-path/credential patterns, README wording/sections, citation identities,
   license, 12 display chains, documentation links, imports and retained adverse
   numerical findings. The verifier fails before importing code if manifest
   validation fails.
5. `CITATION.cff` validates against the official 1.2.0 JSON Schema, using a
   separately installed packaging-only validator. See citation_validation.json.
   No DOI, publication acceptance or repository archive identifier is invented.
6. Included aggregate numerical files are byte-identical to their source files.
   The forecast file is a string-preserving projection, and configuration scalar
   values match source parameters. Method bodies retain their computational
   expressions; only import routing, documentation and selected API packaging
   were changed. This is not a new validation of the scientific theory.

|Required scientific lock|Result|
|---|---|
|Scientific result modifications|0|
|New experiments / resampling|0 / 0|
|New simulator calls|0|
|Post-hoc tuning|0|
|Manuscript table/figure artifact hashes match source|YES|
|Adverse results and reference-status qualifications retained|YES|

## Data and reproduction boundary

Display reproduction is self-contained. Full historical simulation reruns are
not turnkey: raw attendance/source records, residual observations and large
experiment banks are not redistributed. The attendance compilation's exact
landing-page provenance remains unresolved and is stated in `data/README.md`.
No raw input is relabeled as licensed merely because its source is public.
The included outputs use finite-reference application truth and externally
calibrated elasticity; no real-market or causal-validation claim is added.

The exclusion inventory is a future archiving plan, not a promise that a Zenodo
deposit already exists. The MIT license applies to code/software documentation,
not rights in excluded third-party data. Unpublished manuscript PDFs and private
working-history folders are not committed.

## Recheck

```text
python scripts/verify_release.py
python scripts/reproduce_main_tables.py
python scripts/reproduce_main_figures.py
```

Outputs go to ignored `build/`. The payload manifest excludes only itself and
non-release directories (`.git`, local environments, caches and `build/`).
Its own self-hash is intentionally absent. The verifier does not replace or
regenerate the expected manifest, so a changed result cannot silently validate.
