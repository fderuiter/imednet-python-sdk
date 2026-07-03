# Refactoring Patterns

This document outlines identified refactoring opportunities to improve code quality, maintainability, and adherence to SOLID principles in the iMednet Python SDK.

## Executive Summary

The SDK has a **solid architectural foundation** with good separation of concerns at the module level. However, there are opportunities to reduce code duplication, improve consistency, and enhance maintainability through targeted refactoring efforts.

**Priority**: Focus on high-impact, low-risk refactorings first.

## Endpoint Composition Standard

Endpoint read operations are implemented with composition, not deep operation mixin inheritance.
Concrete endpoints inherit **only** from `EdcGenericListGetEndpoint` — a single base class that
combines the EDC path prefix and study-key injection with the full list/get composition provided
by `GenericListGetEndpoint`.

```python
from imednet.core.endpoint.edc_mixin import EdcGenericListGetEndpoint
from imednet.models.records import Record


class RecordsEndpoint(EdcGenericListGetEndpoint[Record]):
    PATH = "records"
    MODEL = Record
    _id_param = "recordId"
```

For path-based `get` behavior, override `get`/`async_get` and compose `PathGetOperation` directly.

## 1. Code Duplication & DRY Violations

### 1.1 Endpoint Class Boilerplate ⚠️ HIGH PRIORITY

**Issue**: Each endpoint class has repetitive configuration. Create specialized base classes (`StudyBoundEndpoint`, `StudyIndependentEndpoint`, `CachedEndpoint`).

### 1.2 Sync/Async Code Duplication ⚠️ MEDIUM PRIORITY

**Issue**: Methods like `RecordsEndpoint.create()` and `RecordsEndpoint.async_create()` have nearly identical logic. Extract shared preparation logic.

## 2. SOLID Principle Violations

### 2.1 Single Responsibility Principle (SRP) ⚠️ HIGH PRIORITY

**Issue**: `ListGetEndpointMixin` handles filter preparation, cache management, pagination, response parsing, and sync/async execution. Split into focused classes.

### 2.2 Open/Closed Principle (OCP) ⚠️ MEDIUM PRIORITY

**Issue**: Error status code mapping is hardcoded. Use a registry pattern for extensibility.

### 2.3 Liskov Substitution Principle (LSP) ⚠️ MEDIUM PRIORITY

**Issue**: Endpoints behave inconsistently regarding `study_key`. Create distinct base classes or use composition.

### 2.4 Dependency Inversion Principle (DIP) ⚠️ LOW PRIORITY

**Issue**: Workflows are tightly coupled to SDK implementation. Define protocols/interfaces.

## 3. Architectural Improvements

### 3.1 Inconsistent Configuration ⚠️ HIGH PRIORITY

**Issue**: Default values scattered. Centralize configuration in an `SDKConfig` object.

### 3.2 Dependency Injection Container ⚠️ MEDIUM PRIORITY

**Issue**: Manual endpoint initialization in SDK is boilerplate-heavy. Implement a simple DI container.

### 3.3 Form Designer Integration ⚠️ MEDIUM PRIORITY

**Issue**: `form_designer/client.py` doesn't use SDK's HTTP client infrastructure.

## 4. Code Quality Issues

### 4.1 Magic Values ⚠️ LOW PRIORITY

Extract magic strings and lists into named constants or enums.

### 4.2 Complex Functions ⚠️ MEDIUM PRIORITY

Apply Extract Method refactoring to functions like `_list_impl()` and long workflow methods.

### 4.3 Exception Handling ⚠️ LOW PRIORITY

Avoid broad exception catches with `pragma: no cover`. Catch specific exceptions instead.
