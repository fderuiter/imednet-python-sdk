# Changelog

## [0.6.0](https://github.com/fderuiter/imednet-python-sdk/compare/imednet-workflows-v0.5.3...imednet-workflows-v0.6.0) (2026-05-27)


### Features

* add records cache and schema profiler scaffolding ([ed64413](https://github.com/fderuiter/imednet-python-sdk/commit/ed64413c1601da46ce357b70c3376b71e040295c))
* add standards profiles and readiness validation ([33356c7](https://github.com/fderuiter/imednet-python-sdk/commit/33356c713b57d4a3091bc093eb14c4f16681fee5))
* add triage schemas, store, and review workbench scaffolding ([45d937b](https://github.com/fderuiter/imednet-python-sdk/commit/45d937b35d340d7ff38d6514fa8eec282e64ef1b))
* finalize records cache and schema profiler ([d02c747](https://github.com/fderuiter/imednet-python-sdk/commit/d02c747dc83dc1dbf1a3f990ffad3a06ac170f5c))
* **governance:** add config version control, publisher wizard, and data lineage modules ([c6bce78](https://github.com/fderuiter/imednet-python-sdk/commit/c6bce78f231959db37cf996fe7026b25bcdde99a))
* **performance:** add sync worker, chunked workflows, and paginated guardrails ([fb76e71](https://github.com/fderuiter/imednet-python-sdk/commit/fb76e71fa2851dda11e8910b55533abe99291616))
* stateful incremental tracker 987 ([#1084](https://github.com/fderuiter/imednet-python-sdk/issues/1084)) ([e67eb80](https://github.com/fderuiter/imednet-python-sdk/commit/e67eb802a32541acf95f90fd1e605559ff1dd96f))
* stream chunked workflow exports ([2feacec](https://github.com/fderuiter/imednet-python-sdk/commit/2feacec8f4921e6fefb9bb70051293686413897d))
* **streamlit:** implement Query Status Overview dashboard page ([#1045](https://github.com/fderuiter/imednet-python-sdk/issues/1045)) ([68b0591](https://github.com/fderuiter/imednet-python-sdk/commit/68b0591ef1b0bcdfadbb50b29f724b98f89ced22))
* **workflows:** add canonical extraction engine ([d78216e](https://github.com/fderuiter/imednet-python-sdk/commit/d78216e08dfcb777bbc8dfb7a91484f6e226d8c6))
* **workflows:** add DuckDBIngestionWorkflow for incremental eCRF bronze/silver centralization ([#1027](https://github.com/fderuiter/imednet-python-sdk/issues/1027)) ([58ffb7b](https://github.com/fderuiter/imednet-python-sdk/commit/58ffb7befb552d1855528abd3584e077e704de61))
* **workflows:** harden config version control ledger integrity ([c6ca772](https://github.com/fderuiter/imednet-python-sdk/commit/c6ca7721f80ae9de0fc18022122c545c9910b4c2))
* **workflows:** harden local triage store with WAL-safe writes, schema migration, and redacted errors ([#1144](https://github.com/fderuiter/imednet-python-sdk/issues/1144)) ([c3d5978](https://github.com/fderuiter/imednet-python-sdk/commit/c3d5978b626962f0bbb54bdb7d08221feb845ba3))


### Bug Fixes

* **governance:** replace old-style generics and improve exception messages in governance modules ([9a346fe](https://github.com/fderuiter/imednet-python-sdk/commit/9a346fecaaf5603da72165631d83af17713ed293))
* serialize SQLite WAL init per DB path to prevent concurrent lock errors ([f6e6991](https://github.com/fderuiter/imednet-python-sdk/commit/f6e69915ea999413e329b8eff9156fc4ff1cdd9c))


### Documentation

* clarify chunked workflow streaming APIs ([fe70965](https://github.com/fderuiter/imednet-python-sdk/commit/fe709657f08a62942e20ba1d05b3b08935418f84))

## [0.5.3](https://github.com/fderuiter/imednet-python-sdk/compare/imednet-workflows-v0.5.2...imednet-workflows-v0.5.3) (2026-05-21)


### Bug Fixes

* tighten sync-async workflow typing boundaries ([5ded1c6](https://github.com/fderuiter/imednet-python-sdk/commit/5ded1c61a65b6376b264d9b9d4dd5658aa78c831))

## [0.5.2](https://github.com/fderuiter/imednet-python-sdk/compare/imednet-workflows-v0.5.1...imednet-workflows-v0.5.2) (2026-05-13)


### Bug Fixes

* tighten workflow init errors and airflow s3 fallback messaging ([b706b3c](https://github.com/fderuiter/imednet-python-sdk/commit/b706b3c04691566b5fd6c632a93eaea30307e419))
