# Changelog

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
