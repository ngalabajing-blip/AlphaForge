# research/

Offline notebooks and one-shot scripts that don't belong inside any
particular service. Outputs are written into `research/output/` and
ignored by git.

* `notebooks/anomaly_eval.py` — evaluate anomaly model variants on a
  synthetic labelled dataset.
* `notebooks/backtest_grid.py` — sweep EMA fast/slow combinations
  and emit a CSV consumed by Grafana / Excel.
