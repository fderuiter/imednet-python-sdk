# Changelog

## [0.6.0](https://github.com/fderuiter/imednet-python-sdk/compare/apache-airflow-providers-imednet-v0.5.2...apache-airflow-providers-imednet-v0.6.0) (2026-05-27)


### Features

* **airflow:** lower provider floor and isolate amazon dependency ([da1af1a](https://github.com/fderuiter/imednet-python-sdk/commit/da1af1a5df9fc299fb2bb1661f56baab76a12d6f))
* extend airflow hook with discovery-safe sdk helpers ([96a024e](https://github.com/fderuiter/imednet-python-sdk/commit/96a024e7761aa57247e30db47dab06985d43b2b7))
* harden airflow export operator mapping ([d5fcf9d](https://github.com/fderuiter/imednet-python-sdk/commit/d5fcf9d7b9cb7e9e123178e01eef381b284d820c))


### Bug Fixes

* **airflow:** require Airflow 3.2+ and harden provider compatibility ([9966b58](https://github.com/fderuiter/imednet-python-sdk/commit/9966b582afcecb6cd99cd6d92af797ba3b4929ef))


### Documentation

* **airflow:** clarify Context import fallback paths ([d3c6d43](https://github.com/fderuiter/imednet-python-sdk/commit/d3c6d43d4ebc5bed1d03e4d4acc460d7e140f9e2))
* clarify airflow export mapping guidance ([074c08d](https://github.com/fderuiter/imednet-python-sdk/commit/074c08d0b842ea59273e7272216bbc0b1ee2d956))

## [0.5.2](https://github.com/fderuiter/imednet-python-sdk/compare/apache-airflow-providers-imednet-v0.5.1...apache-airflow-providers-imednet-v0.5.2) (2026-05-13)


### Bug Fixes

* address PR review thread issues for plugin loading and docs refs ([2c841e0](https://github.com/fderuiter/imednet-python-sdk/commit/2c841e0288a206af737891904ee00c4b7fc666a4))
* require patched apache-airflow release ([549f82a](https://github.com/fderuiter/imednet-python-sdk/commit/549f82a68186e6417f2088e7c60c83b1aabf96f5))
* stabilize workspace dependency validation ([9b7799f](https://github.com/fderuiter/imednet-python-sdk/commit/9b7799f8c138b009cf92bed97f031bd5d29615da))
* tighten workflow init errors and airflow s3 fallback messaging ([b706b3c](https://github.com/fderuiter/imednet-python-sdk/commit/b706b3c04691566b5fd6c632a93eaea30307e419))
