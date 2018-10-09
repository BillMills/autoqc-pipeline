Containerized pipeline to amend a previously-run qc database with some new tests, and return performance and discrimination stats and plots. Usage:

```
docker container run -it -v $(pwd)/new-tests:/AutoQC/dev thisimage
```

where `$(pwd)/new-tests/qctests` has the new qc tests to be integrated. All analysis artefacts will be dumped to `$(pwd)/new-tests`.
