# Changelog

## [0.8.0](https://github.com/fderuiter/imednet-python-sdk/compare/imednet-v0.7.0...imednet-v0.8.0) (2026-05-27)


### Features

* add atomic staged parquet partition writes ([01276aa](https://github.com/fderuiter/imednet-python-sdk/commit/01276aa3afe8a5e980d86c0c3e4e175167b54f09))
* add pyarrow dataset partitioned parquet engine ([4c8a630](https://github.com/fderuiter/imednet-python-sdk/commit/4c8a630ffbcd9d71e369239346e7488b83d2234a))
* add standards profiles and readiness validation ([33356c7](https://github.com/fderuiter/imednet-python-sdk/commit/33356c713b57d4a3091bc093eb14c4f16681fee5))
* add triage schemas, store, and review workbench scaffolding ([45d937b](https://github.com/fderuiter/imednet-python-sdk/commit/45d937b35d340d7ff38d6514fa8eec282e64ef1b))
* **cli:** add `imednet export duckdb` subcommand with filter passthrough and dependency guard ([#1028](https://github.com/fderuiter/imednet-python-sdk/issues/1028)) ([1fee464](https://github.com/fderuiter/imednet-python-sdk/commit/1fee464a9379809056d585c202328919d107fb8d))
* **cli:** register `imednet dashboard` with optional-plugin fallback and launcher ([#1030](https://github.com/fderuiter/imednet-python-sdk/issues/1030)) ([2d868f3](https://github.com/fderuiter/imednet-python-sdk/commit/2d868f38111deb90bd3ada0b95abbcee16cc06fb))
* **core:** add arrow table serialization utility ([73d8cfe](https://github.com/fderuiter/imednet-python-sdk/commit/73d8cfe25d66202b17739a3928a44fbc39adc519))
* **core:** add duckdb and other export dependencies as optional extras ([e2fc72b](https://github.com/fderuiter/imednet-python-sdk/commit/e2fc72ba8d16d19d7c509074916c4b63c4f92eb6))
* **core:** add export helpers and CLI commands for mongodb neo4j and snowflake ([018f880](https://github.com/fderuiter/imednet-python-sdk/commit/018f88087f4cd79afca08f6dba1ca37dbfcfdaab))
* **core:** add Hive-partitioned Parquet export helpers for concurrent analytical extraction ([#1023](https://github.com/fderuiter/imednet-python-sdk/issues/1023)) ([09cf8e5](https://github.com/fderuiter/imednet-python-sdk/commit/09cf8e5416bc6042a56802be801e2ffe2535d0a1))
* **core:** add native DuckDB export APIs for full-study and per-form integrations ([#1024](https://github.com/fderuiter/imednet-python-sdk/issues/1024)) ([3c2c5da](https://github.com/fderuiter/imednet-python-sdk/commit/3c2c5daf4656a1ff7729130e38115dc4684e98bf))
* **core:** enrich mongodb export envelopes with canonical metadata ([2b740bd](https://github.com/fderuiter/imednet-python-sdk/commit/2b740bd1e17e4073606f76b9daf87440ec984ab6))
* **core:** export MultiStudyOrchestrator and orchestration types from top-level `imednet` API ([#1043](https://github.com/fderuiter/imednet-python-sdk/issues/1043)) ([e142a0e](https://github.com/fderuiter/imednet-python-sdk/commit/e142a0e4a112b469553ab832676e7f8c9cbd3732))
* **core:** export sink architecture for Neo4j, MongoDB, and Snowflake ([#1109](https://github.com/fderuiter/imednet-python-sdk/issues/1109)) ([919a004](https://github.com/fderuiter/imednet-python-sdk/commit/919a004e7503dfdc31b226f43f6a6771a4f74830))
* **core:** harden parquet commit failure cleanup ([776c4bf](https://github.com/fderuiter/imednet-python-sdk/commit/776c4bf2417bbce09212ab3420210376d957c948))
* **errors:** introduce orchestration-specific error types in `imednet.errors` ([#1035](https://github.com/fderuiter/imednet-python-sdk/issues/1035)) ([158e483](https://github.com/fderuiter/imednet-python-sdk/commit/158e483f600a4cb2ef11910bbd8aa0ce807c88b5))
* finalize pyarrow partitioned storage engine integration ([e2e661d](https://github.com/fderuiter/imednet-python-sdk/commit/e2e661d0875310bd39d3d0842ac03190c092cece))
* **models:** add study configuration schemas for reporting ([b2098f3](https://github.com/fderuiter/imednet-python-sdk/commit/b2098f380fd8511a25f7136a54dc4e53d5656bd2))
* **orchestration:** add `studyKey` log context alias to multi-study worker telemetry ([#1073](https://github.com/fderuiter/imednet-python-sdk/issues/1073)) ([9a652b9](https://github.com/fderuiter/imednet-python-sdk/commit/9a652b9fedfacabe54a0e5b0d68448c3cc6ea1b2))
* **orchestration:** add concurrent `execute_pipeline` with per-study isolation and normalized results ([#1038](https://github.com/fderuiter/imednet-python-sdk/issues/1038)) ([d1a6b3f](https://github.com/fderuiter/imednet-python-sdk/commit/d1a6b3f47569b8b962a5d698f9a9517e79457f07))
* **orchestration:** add StudyContextLogAdapter for per-study log enrichment ([#1036](https://github.com/fderuiter/imednet-python-sdk/issues/1036)) ([9d27585](https://github.com/fderuiter/imednet-python-sdk/commit/9d275859e0ea4e4ed74eaf85d463e25b978d1bc7))
* **orchestration:** add typed worker protocol and normalized result schema for orchestrator contracts ([#1031](https://github.com/fderuiter/imednet-python-sdk/issues/1031)) ([fd7cdde](https://github.com/fderuiter/imednet-python-sdk/commit/fd7cddeb0b3f1f60a7e7a71ec1dfe233f12538f1))
* **orchestration:** implement MultiStudyOrchestrator initialization and active-study filter resolution ([#1037](https://github.com/fderuiter/imednet-python-sdk/issues/1037)) ([b7d4660](https://github.com/fderuiter/imednet-python-sdk/commit/b7d46606c146933788e30d7f1dec58a05dcccb80))
* **orchestration:** propagate study_context() into ThreadPoolExecutor worker threads ([#1041](https://github.com/fderuiter/imednet-python-sdk/issues/1041)) ([d1df7be](https://github.com/fderuiter/imednet-python-sdk/commit/d1df7be70d17c40638770debdab7d9bf478c8887))
* **orchestration:** scaffold `imednet.orchestration` package namespace and public surface ([#1026](https://github.com/fderuiter/imednet-python-sdk/issues/1026)) ([73bdd32](https://github.com/fderuiter/imednet-python-sdk/commit/73bdd321f57d540443381445dbdd08824a15610b))
* **performance:** add sync worker, chunked workflows, and paginated guardrails ([fb76e71](https://github.com/fderuiter/imednet-python-sdk/commit/fb76e71fa2851dda11e8910b55533abe99291616))
* stream chunked workflow exports ([2feacec](https://github.com/fderuiter/imednet-python-sdk/commit/2feacec8f4921e6fefb9bb70051293686413897d))
* validate reporting profile names ([14422c3](https://github.com/fderuiter/imednet-python-sdk/commit/14422c343b3c8349fdea370d24329ee1d323bd92))


### Bug Fixes

* align snowflake import guidance ([20ecd6a](https://github.com/fderuiter/imednet-python-sdk/commit/20ecd6ae2ef6e1c6aed6c2a9509366b9644173ab))
* **analytics:** exercise DuckDB and Hive-Parquet paths in the default CI/dev environment ([#1034](https://github.com/fderuiter/imednet-python-sdk/issues/1034)) ([17c7fa8](https://github.com/fderuiter/imednet-python-sdk/commit/17c7fa8b7d279105a8336c00b2dc1f666b47a18a))
* **core:** address export CLI and sink review follow-ups ([4ac2d95](https://github.com/fderuiter/imednet-python-sdk/commit/4ac2d958326b2f9f6f4920e5c902ed1941bed7b1))
* **parquet:** enable union-by-name hive parquet query ([829cf66](https://github.com/fderuiter/imednet-python-sdk/commit/829cf66b0b29c17cda60535e706538f7a9fe7484))
* validate hive partition keys before writing parquet ([1e1d2a5](https://github.com/fderuiter/imednet-python-sdk/commit/1e1d2a54ff05021add48768acb43b1766b80d801))


### Documentation

* clarify chunked workflow streaming APIs ([fe70965](https://github.com/fderuiter/imednet-python-sdk/commit/fe709657f08a62942e20ba1d05b3b08935418f84))
* **orchestration:** Sphinx API reference, module docstrings, and multi-study pipeline example ([#1047](https://github.com/fderuiter/imednet-python-sdk/issues/1047)) ([b3a61de](https://github.com/fderuiter/imednet-python-sdk/commit/b3a61dee38a34b1cff4fbc70059fdf9c9f0c3c1b))

## [0.7.0](https://github.com/fderuiter/imednet-python-sdk/compare/imednet-v0.6.2...imednet-v0.7.0) (2026-05-21)


### Features

* **plugins:** add PluginProtocol, PluginLoadError, plugin authoring docs and tests ([19a977b](https://github.com/fderuiter/imednet-python-sdk/commit/19a977b825ba80e0d5f418ce4a143c687782083f))


### Bug Fixes

* fully suppress httpx/httpcore logs during request execution ([d8f264e](https://github.com/fderuiter/imednet-python-sdk/commit/d8f264ed00b55c7c77abb2b0e26c40b74bd7d130))
* harden credential redaction in auth, errors, transport, and CLI tests ([fddefc0](https://github.com/fderuiter/imednet-python-sdk/commit/fddefc0401ba17967abcc4f7b46c3f90555f9bfa))
* **http:** normalize encoded path segments safely ([e6e7489](https://github.com/fderuiter/imednet-python-sdk/commit/e6e748951ec60f1c4d349ed6bc7a00035d040767))
* improve redaction matching and simplify log suppression ([000c46f](https://github.com/fderuiter/imednet-python-sdk/commit/000c46fd2cef1ce54d8173e8769e937a6af93be5))
* **plugins:** remove redundant pass in PluginLoadError body ([d3f20e9](https://github.com/fderuiter/imednet-python-sdk/commit/d3f20e91649b73572abb699464f612996c71fb7c))
* refine paginator cursor state semantics ([8d205e7](https://github.com/fderuiter/imednet-python-sdk/commit/8d205e7ebd8f69c032249d475a6e38c39fbb2fce))
* tighten paginator cursor validation message formatting ([257a1b6](https://github.com/fderuiter/imednet-python-sdk/commit/257a1b6d741a6e0b60a689a7b20116039fc4e54a))


### Documentation

* ✍️ Scribe: fix broken optional dependency installation commands ([20ae098](https://github.com/fderuiter/imednet-python-sdk/commit/20ae09880daf9ca7430f34d5a3a9baa70071ef6d))

## [0.6.2](https://github.com/fderuiter/imednet-python-sdk/compare/imednet-v0.6.1...imednet-v0.6.2) (2026-05-19)


### Bug Fixes

* remove stateful instance caching from endpoints for thread-safety ([1b8acb4](https://github.com/fderuiter/imednet-python-sdk/commit/1b8acb4e0244090f3034dc3d8057f191d1d0cdb4))

## [0.6.1](https://github.com/fderuiter/imednet-python-sdk/compare/imednet-v0.6.0...imednet-v0.6.1) (2026-05-13)


### Bug Fixes

* resolve workspace package build metadata ([9f3be6c](https://github.com/fderuiter/imednet-python-sdk/commit/9f3be6c642944a09cdb151152ec8d6788dd34d3b))
* stabilize workspace dependency validation ([9b7799f](https://github.com/fderuiter/imednet-python-sdk/commit/9b7799f8c138b009cf92bed97f031bd5d29615da))
* use package-local core readme for builds ([d672c5f](https://github.com/fderuiter/imednet-python-sdk/commit/d672c5fe6afd85a04ffa0b8814115685778c5e92))
