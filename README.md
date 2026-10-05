# Near-Optimal Screening under Fixed Simulation Budgets: Preservation, Efficiency, and the Role of Common Random Numbers

This repository contains reproducibility materials for the manuscript
"Near-Optimal Screening under Fixed Simulation Budgets: Preservation,
Efficiency, and the Role of Common Random Numbers."

The study compares fixed-sample and adaptive screening procedures under
fixed simulation budgets, with particular attention to near-optimal set
preservation, screening efficiency, final recommendation performance, and
the use of common random numbers.

## Overview

Preservation and recommendation are different objectives. Retaining every
near-optimal alternative does not ensure that the final recommendation is good,
and high recommendation accuracy can coexist with incorrect elimination.
No screening architecture dominates across all objectives and settings.

This repository reproduces the five main tables and seven main figures from
stored verified outputs. It also provides the computational kernels,
prespecified configurations, seed rules and complete aggregate result matrices.
Display reproduction needs neither raw WNBA records nor large experiment banks.
Full simulation reruns require separately acquired inputs and excluded banks;
they are not performed by the reproduction commands below.

## Repository structure

```text
src/                 Simulator, CPC, baselines and metric implementations
configs/             Formal, robustness and external-comparator specifications
scripts/             Table/figure reproduction and release verification
data/                Derived forecasts, known Gaussian means and source documentation
results/main_tables/ Approved main-table TeX
results/main_figures/Approved figure PNG, PDF and editable SVG
results/machine_readable/ Numerical summaries and exact display-row CSVs
supplement/          Guide to complete aggregate matrices and metric definitions
reproducibility/     Hash manifest, source comparisons, traceability and seed rules
submission/          Author-provided declaration drafts
```

## Main methods

|Method|Role and boundary|
|---|---|
|CPC (epsilon-CPC-SH)|Adaptive certification with fresh batches, a predictable anchor, Holm correction and summable stage error spending|
|DSTTB|Published fixed-sample, set-wise double-sided test-to-the-best; independence-calibrated comparator used with CRN OFF|
|B1|Bonferroni marginal-box screening; dependence-valid under the marginal interval assumptions, without covariance-based narrowing|
|B2|Standardized paired Bonferroni adaptation for this comparison; not a published DSTTB algorithm|
|Uniform, SH, SR, OCBA|Recommendation-oriented allocation baselines; SH denotes the halving baseline only|
|Bounded CPC|Bounded-confidence comparator; its bounded-data interpretation is not transferred to unbounded Gaussian data|

The conditional Gaussian preservation theory is separate from recommendation
accuracy. The independent-stream Welch test is approximate; non-Gaussian results
are empirical stress evidence. No distribution-free or universal superiority
claim is made. The [external-comparator notes](configs/external_comparators/README.md)
identify the published rule and the two adaptations.

## Experimental settings

|Study|Budgets|Selections per cell|Truth or reference|
|---|---|---|---|
|Gaussian formal experiments|256, 512, 1024|5,000|Known means; three correlation regimes|
|WNBA formal experiments|256, 512, 1024|300|20,000-path finite reference per policy|
|Direct external comparison|512|Gaussian: 1,000; WNBA: 200|Same definitions, independent CPC and comparator banks|
|Tolerance sensitivity|256, 512, 1024|200 at added tolerances; 300 reused at baseline|Same finite WNBA reference|
|Structural sensitivity|512|60 per new scenario; 300 reused at baseline|3,000 paths per new scenario|
|Non-Gaussian stress|256, 512, 1024|5,000|Known means; heavy-tailed and skewed components|

All formal comparisons use 32 alternatives. One alternative–replication output
is one charged call, including initialization, confidence sampling and terminal
refinement. Sharing a CRN path does not reduce charged cost. Reference-bank costs
are separate. Tolerances are 0.25%, 0.50% and 1.00% of the fixed calibration scale
where applicable. See the configurations for full precision and interval rules.

## WNBA simulation benchmark

The application is an empirically informed dynamic revenue-management simulator
with finite inventory, stochastic demand, updated forecasts and policy-dependent
pricing feedback. It covers 263 scheduled games with decision windows at 30, 14,
7, 3, 1 and 0 days before each game. Price elasticity is externally calibrated,
with baseline 1.2; it is not estimated from transaction-level WNBA prices.

WNBA results are **simulation-benchmark results**, evaluated against **finite
simulation reference estimates**, not population truth. The benchmark does not
establish real-world optimal ticket prices, causal elasticity or operational
validation. Structural experiments change one factor at a time. Venue capacities
and a year-level price proxy are imperfect modeling inputs.

## Reproducing tables

Use Python 3.14.4 and the observed dependency versions in `requirements.txt`:

```bash
python -m venv .venv
# Activate .venv using your operating system's activation command.
python -m pip install -r requirements.txt
python scripts/verify_release.py
python scripts/reproduce_main_tables.py
```

The table command writes to `build/main_tables/` and verifies equality with the
approved TeX artifacts. Tables 3–4 additionally recompute display formatting
from the full-precision numerical summaries. Tables 1–2 are method/design
descriptions; Table 5 is an editorial selection of adverse evidence. Their exact
display-row CSVs and evidence links are provided. No estimates are refitted.

## Reproducing figures

```bash
python scripts/reproduce_main_figures.py
```

This writes seven figures in PNG, PDF and SVG to `build/main_figures/`, then
compares PNG pixels with the approved figures. The verified environment produces
identical PNG pixels. Different fonts or plotting versions may affect rendering;
a discrepancy is reported rather than replacing approved files. PDF/SVG metadata
can differ. Both commands accept `--output-dir`; they refuse destinations inside
the approved `results/` tree. Typical runtime is seconds for tables and under
one minute for figures. No simulator, bootstrap or random experiment is invoked.

## External comparator analysis

The direct comparison was prespecified at the intermediate budget 512 and does
not establish full-budget dominance. CRN ON shares exogenous paths across
alternatives **within a procedure**; CRN OFF uses independent alternative-specific
streams. CPC-versus-comparator inference is algorithm-level unpaired because
the banks are independent. B1 and B2 share their external bank; their displayed
marginal intervals are not an interval for a B1-minus-B2 contrast.

Published DSTTB retains fewer alternatives than CPC in the Gaussian independent
case. Under strong positive CRN, paired B2 and CPC screen much more strongly
than marginal B1. B2 can retain fewer survivors than CPC. Weak dependence need
not improve adaptive screening. Adverse OCBA contrasts, strict-tolerance
preservation failures and shared recommendation ceilings remain in the results.

## Data provenance

[data/README.md](data/README.md) documents the public-source attendance compilation,
official single-game supplement, venue sources, derived inputs and the rights
boundary. Only author-generated forecasts, known Gaussian means and simulation
summaries are distributed. Raw third-party tables, scraped pages and private data
are excluded. The historical attendance compilation's upstream landing-page
provenance is incomplete; the repository does not invent a source URL or promise
an exact raw-data rebuild from an unverified replacement. This does not affect
reproduction of the included manuscript displays.

## Computational environment

The observed environment is Python 3.14.4 with NumPy, SciPy, pandas, Matplotlib,
PyYAML and Pillow. Versions are pinned from the verified local environment, not
guessed. Only packages actually imported by the included code are direct
requirements. LaTeX is unnecessary to generate or verify table source; compiling
the TeX tables elsewhere requires `booktabs` and `tabularx`.

## Reproducibility notes

- Version `1.0.0-submission` is documented in the
  [release notes](RELEASE_NOTES.md) and [Zenodo metadata](ZENODO_METADATA.md).
  The archival DOI is pending.
- [Traceability](reproducibility/traceability.csv) links every main display to its
  machine-readable input, generating script, configuration and seed/reference source.
- [Verification report](reproducibility/verification_report.md) records the build,
  hashes, import checks and display comparisons. Scientific values changed: 0;
  new experiments: 0; new simulator calls: 0.
- [SHA-256 manifest](reproducibility/SHA256_MANIFEST.csv) covers repository payload
  files; its own hash is excluded to avoid a circular dependency.
- Original method identifiers and opaque seed labels remain in machine-readable
  evidence where changing them would break traceability. Human-facing method names
  are mapped in [the results guide](supplement/README.md).
- [Excluded artifacts](reproducibility/excluded_artifacts.csv) identifies large banks
  and raw inputs for a future rights-reviewed archive. No Zenodo DOI is assigned.

## Citation

Beichen Lin and Maodong Zhang. *Near-Optimal Screening under Fixed Simulation Budgets: Preservation, Efficiency, and the Role of Common Random Numbers*. Manuscript, 2026.

Use [CITATION.cff](CITATION.cff) for machine-readable citation metadata.
No publication DOI or acceptance status is asserted.

## License

The authors selected the [MIT License](LICENSE) for the code and accompanying
software documentation. The [standard MIT text](https://opensource.org/license/mit)
does not assign rights in separately owned third-party source data; see the data policy.

## Contact

**Beichen Lin**, corresponding author — School of Science, Minzu University of
China, Beijing, China. Email: beichenlin693@gmail.com.
[ORCID: 0009-0003-2486-0718](https://orcid.org/0009-0003-2486-0718).

**Maodong Zhang** — Software Engineering, Xinjiang University, Urumqi, Xinjiang,
China. Email: 2132257382@qq.com.
