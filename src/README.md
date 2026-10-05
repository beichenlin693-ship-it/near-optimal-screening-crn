# Computational kernels

The library contains the simulator dynamics, 32-policy family, explicit random
path machinery, adaptive CPC rule, recommendation baselines, fixed-sample
screening rules and metric calculations. Imports have no simulation side effects.

```python
from src.screening.cpc import run
from src.baselines.fixed_sample import screen
from src.simulator.simulator import simulate
from src.simulator.inputs import Inputs
from src.simulator.policy_pool import policies
```

These are scientific library APIs, not automatic experiment runners.
`screen(x, epsilon, method)` consumes an existing n-by-K matrix. Adaptive
`run(context, epsilon)` consumes an explicit sampling callback through
`src.baselines.common.RunContext`; the context charges alternative–replication
evaluations. `RunContext` is the bounded-reward context for the revenue simulator,
not a drop-in unbounded Gaussian context. `simulate(policy, path, inputs, config)`
requires explicit authorized input data and a supplied exogenous path. Calling
these APIs can perform new scientific computation; none is called by the
display-reproduction or release-verification commands.

Original opaque method/seed identifiers are preserved where they affect stored
records or random streams. The computational expressions and selected scientific
function bodies match the approved source after documented import/packaging
adjustments. `reproducibility/code_equivalence.json` states the exact comparison
scope. Source files include their own concise input/output/runtime headers.

`metrics/selection.py` retains an earlier generic summary interface; its status
field is not a formal-study label. The formal interval formulas are in
`metrics/statistics.py`, and the included result CSVs are authoritative for the
paper. No metric or confidence interval is newly estimated during packaging.
