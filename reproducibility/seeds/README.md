# Seed and reference conventions

`namespaces.json` stores the original opaque labels verbatim. Altering their
spelling, method keys, index origin or concatenation changes a random stream.
The simulator base seed is 20260930. `src/simulator/path_bank.py` defines domain
IDs, path keys and 128-bit SHA-256-derived replication IDs;
`src/simulator/exogenous.py` defines the original explicit path generator.
Synthetic and bootstrap streams use NumPy PCG64 with the first 16 bytes of a
SHA-256 label hash interpreted as an unsigned big-endian integer.

Formal selections cover macro IDs 0–299 (WNBA) and 0–4999 (Gaussian). The direct
external comparison uses the original 0–199 WNBA and 0–999 Gaussian prefixes.
The external fixed-sample observations come from the corresponding Uniform bank;
CPC uses its original independent method stream. No CPC rerun creates a matched
algorithm bank. Tolerance and structural runs use their separate namespaces,
sample counts and scenario labels in the configurations. Baseline cells reused
in robustness summaries are not additional independent draws.

Formal reference estimates use 20,000 paths per policy; new structural references
use 3,000 per scenario. Full reference/sample banks are excluded from this Git
repository and listed for later archiving. Seed formulas alone do not guarantee
bitwise replay without identical source inputs, versions and draw order.
Display-reproduction scripts consume stored aggregates and never draw random samples.
