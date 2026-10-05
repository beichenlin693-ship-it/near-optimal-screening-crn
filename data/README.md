# Data provenance and access policy

The repository distributes author-generated simulation summaries, known Gaussian
means and a minimal projection of derived demand forecasts. It does not distribute
raw third-party data, downloaded pages/PDFs, private records or transaction data.
Public accessibility is not treated as redistribution permission.

## Public sources used

|Input|Recorded provenance and use|Distribution decision|
|---|---|---|
|Historical attendance and schedule compilation|A Kaggle attendance compilation, historically stored as `wnba_attendance_alltime.csv`; 2008 onward. The retained source file has Date, Opponent, Segment, Arena, Location, Attendance, Home Team and Year columns. Its exact uploader/landing-page and original upstream provenance are not established in the retained metadata.|Raw CSV excluded. Do not identify it as official league data or assign an unverified license.|
|Commissioner's Cup final, 25 June 2024|[Official scorer's report](https://statsdmz.nba.com/pdfs/20240625/20240625_MINNYL_book.pdf); supplied the one game absent from the attendance compilation.|Only source link retained; no report or copied row redistributed.|
|Venue capacities|Official venue, league, municipal, university and technical-document sources listed individually in [venue_sources.csv](provenance/venue_sources.csv). Some configurations were uncertain; capacity is not verified event sellable inventory.|Source URLs/titles and authors' uncertainty classification only; no downloaded documents or raw capacity table.|
|Annual price scale|Previously assembled year-level ticket-price proxy; it is a structural scale, not realized transaction prices. Underlying redistribution rights and full source chain are not established here.|Raw price compilations excluded; numerical experimental settings remain in the study configuration/results.|

## Included derived inputs

- `derived/gaussian_means.csv`: exact prespecified Gaussian means, gaps and known
  near-optimal membership; no observations or third-party data.
- `derived/window_demand_forecasts.csv`: exact stored string values for game ID,
  days-to-game and model-generated demand forecast. This is a column projection
  from the approved derived artifact; it was not refitted. It excludes observed
  attendance, dates, teams, lagged attendance features and copied source fields.
- `../results/machine_readable/`: complete included aggregate performance,
  reference-precision and sensitivity tables; manuscript display rows are a
  separate clearly identified presentation layer.

No training records, residual observations, raw demand model inputs, raw source
documents or individual-level private data are supplied. A forecast is not an
observed transaction or an empirical demand curve.

## Obtaining non-redistributed inputs

1. Contact the corresponding author for the original attendance-compilation
   acquisition record and rights status. Locate the exact historical file via its
   recorded filename and SHA-256 in the excluded-artifact inventory. No exact
   public download can currently be promised from the incomplete metadata.
2. Where source terms permit access, consult the official scorer's report for
   the missing Cup game and each original venue URL. Preserve access dates,
   raw file hashes, game identifiers, game-date matching and uncertainty labels.
   A changed live source does not automatically reproduce a historical snapshot.
3. Build the same canonical 263-game schedule and map legally acquired metadata
   to `src.simulator.state.GameInput`. Retain the Cup game and scheduled venue
   overrides; do not substitute observed attendance for inventory.
4. Use only information strictly earlier than each decision date when creating
   forecasts. Reproducing the original model fit additionally requires the
   non-redistributed training data, out-of-sample residual pool and exact feature
   transformations. Supplied forecast outputs avoid refitting for inspection,
   but do not license or replace those original source records.
5. Assemble `src.simulator.inputs.Inputs` with authorized game metadata, the
   original positive out-of-sample shock ratios, dispersion and derived forecast
   lookup. `configs/formal_experiments/simulator.json` preserves computational
   parameters. Model fitting, new random paths and new simulation evaluations are
   separate scientific work and are never triggered by reproduction commands.

Full historical experiment reruns are not a turnkey feature of this lightweight
release because source rights/provenance and the large observation banks remain
outside it. The display-level reproduction and hash checks are self-contained.
Alternative newly acquired data must be labeled a new dataset, not claimed to
reproduce the original study exactly.

## Interpretation

Application performance is evaluated against finite simulation reference
estimates, not population truth. Baseline elasticity is externally calibrated at
1.2, inventory is finite and price inputs are proxies. Reference uncertainty,
one-factor structural sensitivity and non-Gaussian empirical stress remain
distinct from a theorem or real-market validation. The MIT code license does not
grant rights to excluded third-party materials.
