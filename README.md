Containerized pipeline to amend a previously-run qc database with some new tests, and return performance and discrimination stats and plots. Run as an interactive environment:

```
docker container run -it -v $(pwd)/new-tests:/AutoQC/dev thisimage bash
```

where `$(pwd)/new-tests/qctests` has the new qc tests to be integrated, and $(pwd)/new-tests/iquod.db has the database with the canonical tests pre-evaluated. All analysis artefacts will be dumped to `$(pwd)/new-tests`.

User scripts:

 - `experimental-qc.sh`: Evaluate AutoQC for the new qc tests, and append results to iquod.db
 - `optimize-classifier.sh`: Run catchall.py, and append a column to iquod.db indicating resulting [T,F]x[P,N] classification for each profile. If `CUSTOM_PERF=1`, skip catchall, and instead copy `/AutoQC/dev/custom_perf.json` in in `catchall.json`'s place
 - `generate-plots.sh`: Generate plots for each testing profile, categorized by [T,F]x[P,N].
 - `perf-uncertainty.sh`: Generate an uncertainty estimate on TPR and FPR by running `optimize-classifier.sh` a bunch of times
