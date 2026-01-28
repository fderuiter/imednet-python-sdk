# Code Refactoring Guide

This document outlines identified refactoring opportunities to improve code quality, maintainability, and adherence to SOLID principles in the iMednet Python SDK.

## Executive Summary

The SDK has a **solid architectural foundation** with good separation of concerns at the module level. However, there are opportunities to reduce code duplication, improve consistency, and enhance maintainability through targeted refactoring efforts.

**Priority**: Focus on high-impact, low-risk refactorings first.

---

## 1. Code Duplication & DRY Violations

### 1.1 Endpoint Class Boilerplate ⚠️ HIGH PRIORITY

**Issue**: Each endpoint class (`sites.py`, `studies.py`, `forms.py`, etc.) has repetitive configuration with similar patterns.

**Current State**:
```python
# Repeated in multiple endpoint files
class SitesEndpoint(ListGetEndpoint[Site]):
    PATH = "sites"
    MODEL = Site
    _id_param = "siteId"
    _pop_study_filter = True
```

**Impact**: 
- ~40% of endpoint code is boilerplate
- Changes to endpoint behavior require updates across multiple files
- Inconsistent behavior between endpoints (e.g., sites vs forms)

**Recommendation**: Create specialized base classes for different endpoint patterns:

```python
# imednet/endpoints/_base_types.py

class StudyBoundEndpoint(ListGetEndpoint[T]):
    """Base for endpoints that require study context."""
    requires_study_key: bool = True
    _pop_study_filter: bool = False

class StudyIndependentEndpoint(ListGetEndpoint[T]):
    """Base for endpoints that work across studies."""
    requires_study_key: bool = False
    _pop_study_filter: bool = True

class CachedEndpoint(ListGetEndpoint[T]):
    """Base for endpoints with local caching (Forms, Studies, etc.)."""
    _cache_name: str
    
    def _update_cache(self, items: List[T]) -> None:
        # Shared caching logic
        ...
```

**Effort**: 8-12 hours  
**Risk**: Medium (requires careful testing of all endpoints)

---

### 1.2 Sync/Async Code Duplication ⚠️ MEDIUM PRIORITY

**Issue**: Methods like `RecordsEndpoint.create()` and `RecordsEndpoint.async_create()` have nearly identical logic.

**Current State**:
```python
def create(self, study_key, records_data, email_notify, schema):
    self._validate_records_if_schema_present(schema, records_data)
    headers = self._build_headers(email_notify)
    # ... rest of logic

async def async_create(self, study_key, records_data, email_notify, schema):
    self._validate_records_if_schema_present(schema, records_data)
    headers = self._build_headers(email_notify)
    # ... rest of logic (async version)
```

**Recommendation**: Extract shared preparation logic:

```python
def _prepare_create_request(self, records_data, email_notify, schema):
    """Prepare and validate request data for create operation."""
    self._validate_records_if_schema_present(schema, records_data)
    headers = self._build_headers(email_notify)
    payload = {"records": records_data}
    return headers, payload

def create(self, study_key, records_data, email_notify=None, *, schema=None):
    headers, payload = self._prepare_create_request(records_data, email_notify, schema)
    return self._client.post(...)

async def async_create(self, study_key, records_data, email_notify=None, *, schema=None):
    headers, payload = self._prepare_create_request(records_data, email_notify, schema)
    return await self._async_client.post(...)
```

**Effort**: 4-6 hours  
**Risk**: Low

---

## 2. SOLID Principle Violations

### 2.1 Single Responsibility Principle (SRP) ⚠️ HIGH PRIORITY

**Issue**: `ListGetEndpointMixin` (300+ lines) handles too many concerns:
- Filter preparation
- Cache management  
- Pagination
- Response parsing
- Both sync and async execution

**Location**: `imednet/endpoints/_mixins.py:179-216`

**Recommendation**: Split into focused classes:

```python
# imednet/endpoints/_filter_builder.py
class FilterBuilder:
    """Builds API filter parameters from Python arguments."""
    def build(self, filters: Dict, study_key: str) -> Dict:
        ...

# imednet/endpoints/_cache_manager.py  
class EndpointCache:
    """Manages local caching of endpoint data."""
    def get(self, key: str) -> Optional[List]:
        ...
    def update(self, key: str, value: List) -> None:
        ...

# imednet/endpoints/_paginator.py
class EndpointPaginator:
    """Handles pagination for list operations."""
    def paginate(self, client, path, params) -> Iterable:
        ...

# Then compose in endpoints
class ListGetEndpoint:
    def __init__(self, ...):
        self._filter_builder = FilterBuilder()
        self._cache = EndpointCache(self._cache_name)
        self._paginator = EndpointPaginator()
```

**Benefits**:
- Each class has one reason to change
- Easier to test in isolation
- More reusable components

**Effort**: 16-20 hours  
**Risk**: High (core refactoring, extensive testing needed)

---

### 2.2 Open/Closed Principle (OCP) ⚠️ MEDIUM PRIORITY

**Issue**: Error status code mapping is hardcoded in core module.

**Location**: `imednet/core/_requester.py:35-42`

```python
STATUS_TO_ERROR: dict[int, type[ApiError]] = {
    400: BadRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    # ... more hardcoded mappings
}
```

**Recommendation**: Use a registry pattern for extensibility:

```python
# imednet/errors/registry.py
class ErrorRegistry:
    """Registry for HTTP status code to error class mappings."""
    
    _mappings: Dict[int, Type[ApiError]] = {}
    
    @classmethod
    def register(cls, status_code: int, error_cls: Type[ApiError]) -> None:
        """Register a custom error class for a status code."""
        cls._mappings[status_code] = error_cls
    
    @classmethod
    def get_error_class(cls, status_code: int) -> Type[ApiError]:
        """Get error class for status code."""
        return cls._mappings.get(status_code, ApiError)

# Register defaults
ErrorRegistry.register(400, BadRequestError)
ErrorRegistry.register(401, UnauthorizedError)
# ...

# Allow users to register custom errors
ErrorRegistry.register(418, TeapotError)  # Example
```

**Effort**: 4-6 hours  
**Risk**: Low

---

### 2.3 Liskov Substitution Principle (LSP) ⚠️ MEDIUM PRIORITY

**Issue**: Endpoints behave inconsistently - some require `study_key`, others don't.

**Example**:
```python
# SitesEndpoint
_pop_study_filter = True
_missing_study_exception = KeyError

# FormsEndpoint  
_pop_study_filter = False
_missing_study_exception = ValueError
```

**Impact**: Cannot reliably substitute one endpoint for another.

**Recommendation**: Create distinct base classes (see 1.1) or use composition:

```python
class StudyBehavior(Protocol):
    """Defines how endpoint handles study context."""
    def validate_study_key(self, key: Optional[str]) -> str:
        ...

class RequiresStudyBehavior:
    def validate_study_key(self, key: Optional[str]) -> str:
        if not key:
            raise ValueError("Study key required")
        return key

class OptionalStudyBehavior:
    def validate_study_key(self, key: Optional[str]) -> str:
        return key or ""

# Inject behavior
class RecordsEndpoint:
    study_behavior: StudyBehavior = RequiresStudyBehavior()
```

**Effort**: 6-8 hours  
**Risk**: Medium

---

### 2.4 Dependency Inversion Principle (DIP) ⚠️ LOW PRIORITY

**Issue**: Workflows are tightly coupled to SDK implementation.

**Location**: `imednet/workflows/record_mapper.py:38-40`

**Recommendation**: Define protocols/interfaces:

```python
# imednet/protocols.py
class IRecordProvider(Protocol):
    """Interface for fetching records."""
    def list_records(self, study_key: str, **filters) -> List[Record]:
        ...

class ISchemaProvider(Protocol):
    """Interface for fetching schemas."""
    def get_schema(self, study_key: str, form_id: int) -> SchemaCache:
        ...

# Workflows depend on protocols, not concrete SDK
class RecordMapper:
    def __init__(
        self, 
        record_provider: IRecordProvider,
        schema_provider: ISchemaProvider
    ):
        ...
```

**Benefits**:
- Easier testing (mock the interface)
- SDK can be swapped with alternative implementation
- Clearer contracts

**Effort**: 10-12 hours  
**Risk**: Medium

---

## 3. Architectural Improvements

### 3.1 Inconsistent Configuration ⚠️ HIGH PRIORITY

**Issue**: Default values scattered across multiple modules.

**Current State**:
- `http_client_base.py:26-27`: timeout=30.0, retries=3
- `constants.py`: DEFAULT_TIMEOUT, DEFAULT_RETRIES
- Multiple sources of truth

**Recommendation**: Centralize all configuration:

```python
# imednet/config.py
@dataclass
class SDKConfig:
    """Centralized SDK configuration."""
    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT
    retries: int = DEFAULT_RETRIES
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR
    page_size: int = DEFAULT_PAGE_SIZE
    
    @classmethod
    def from_env(cls) -> "SDKConfig":
        """Load configuration from environment variables."""
        return cls(
            base_url=os.getenv("IMEDNET_BASE_URL", DEFAULT_BASE_URL),
            timeout=float(os.getenv("IMEDNET_TIMEOUT", DEFAULT_TIMEOUT)),
            ...
        )

# Usage
config = SDKConfig()
client = Client(config=config)
```

**Effort**: 6-8 hours  
**Risk**: Medium

---

### 3.2 Dependency Injection Container ⚠️ MEDIUM PRIORITY

**Issue**: Manual endpoint initialization in SDK is boilerplate-heavy.

**Current State** (`sdk.py:181-184`):
```python
self.records = RecordsEndpoint(self._client, self._context, self._async_client)
self.forms = FormsEndpoint(self._client, self._context, self._async_client)
# ... 15+ more lines
```

**Recommendation**: Implement DI container:

```python
# imednet/di.py
class Container:
    """Dependency injection container."""
    
    def __init__(self, client, context, async_client):
        self._client = client
        self._context = context
        self._async_client = async_client
    
    def resolve(self, endpoint_cls: Type[T]) -> T:
        """Instantiate endpoint with dependencies."""
        return endpoint_cls(self._client, self._context, self._async_client)

# In SDK
self._container = Container(self._client, self._context, self._async_client)
self.records = self._container.resolve(RecordsEndpoint)
self.forms = self._container.resolve(FormsEndpoint)
```

**Benefits**:
- Less boilerplate
- Easier to add new dependencies
- Testable

**Effort**: 8-10 hours  
**Risk**: Medium

---

### 3.3 Form Designer Integration ⚠️ MEDIUM PRIORITY

**Issue**: `form_designer/client.py` doesn't use SDK's HTTP client infrastructure.

**Impact**:
- Bypasses retry logic
- No span tracking
- Duplicate header management
- Inconsistent error handling

**Recommendation**: Refactor to use `httpx.Client` from SDK or create a shared base:

```python
# Option 1: Inherit from HTTPClientBase
class FormDesignerClient(HTTPClientBase):
    def __init__(self, base_url: str, phpsessid: str, **kwargs):
        super().__init__(**kwargs)
        self.phpsessid = phpsessid
        self._custom_headers = {
            "Cookie": f"PHPSESSID={phpsessid}",
            "X-Requested-With": "XMLHttpRequest",
        }

# Option 2: Composition
class FormDesignerClient:
    def __init__(self, sdk_client: Client, phpsessid: str):
        self._client = sdk_client
        self.phpsessid = phpsessid
```

**Effort**: 6-8 hours  
**Risk**: Medium

---

## 4. Code Quality Issues

### 4.1 Magic Values ⚠️ LOW PRIORITY

**Locations**:
- `endpoints/_mixins.py:207`: Hardcoded pagination class selection
- `endpoints/records.py:59-60`: Magic string checks for newlines

**Recommendation**: Extract to named constants or enums:

```python
# imednet/constants.py
NEWLINE_CHARS = frozenset(["\n", "\r"])

# Usage
if any(char in email_notify for char in NEWLINE_CHARS):
    raise ValueError("email_notify must not contain newlines")
```

**Effort**: 2-3 hours  
**Risk**: Very Low

---

### 4.2 Complex Functions ⚠️ MEDIUM PRIORITY

**Issue**: Some functions exceed cognitive complexity limits.

**Locations**:
- `endpoints/_mixins.py:179-216` `_list_impl()` - 38 lines, multiple concerns
- `workflows/record_mapper.py:130-200` - Long method with nested try-catch

**Recommendation**: Apply Extract Method refactoring:

```python
# Before: _list_impl() does everything
def _list_impl(self, ...):
    # 38 lines of pagination, caching, parsing...

# After: Split into smaller methods
def _list_impl(self, ...):
    items = self._get_from_cache_or_fetch(...)
    return self._parse_items(items)

def _get_from_cache_or_fetch(self, ...):
    if cached := self._get_from_cache(...):
        return cached
    return self._fetch_all_pages(...)

def _fetch_all_pages(self, ...):
    # Pagination logic only
    ...
```

**Effort**: 4-6 hours  
**Risk**: Low

---

### 4.3 Exception Handling ⚠️ LOW PRIORITY

**Issue**: Broad exception catches with `pragma: no cover`.

**Location**: `workflows/record_mapper.py:130-200`

```python
try:
    # complex logic
except Exception:  # Too broad!
    # pragma: no cover
    logger.error(...)
```

**Recommendation**: Catch specific exceptions:

```python
try:
    # complex logic
except (ValidationError, KeyError, ApiError) as e:
    logger.error(f"Failed to process record: {e}")
    raise WorkflowError(...) from e
```

**Effort**: 2-3 hours  
**Risk**: Very Low

---

## 5. Implementation Roadmap

### Phase 1: Quick Wins (1-2 weeks) ✅ DONE
- [x] Extract HTTP headers to constants ✅
- [x] Fix import ordering ✅
- [x] Remove unused imports ✅
- [ ] Extract magic values to constants
- [ ] Improve exception handling

### Phase 2: Foundation (2-3 weeks)
- [ ] Create specialized endpoint base classes
- [ ] Implement configuration object
- [ ] Extract sync/async duplication
- [ ] Add error registry

### Phase 3: Architecture (3-4 weeks)  
- [ ] Split ListGetEndpointMixin (SRP)
- [ ] Implement dependency injection container
- [ ] Refactor Form Designer integration
- [ ] Add protocol-based interfaces

### Phase 4: Polish (1-2 weeks)
- [ ] Refactor complex functions
- [ ] Comprehensive testing of refactored code
- [ ] Update documentation
- [ ] Performance benchmarking

---

## 6. Testing Strategy

For each refactoring:

1. **Write characterization tests** before changing code
2. **Refactor incrementally** - one change at a time
3. **Run full test suite** after each change
4. **Check test coverage** - maintain ≥90%
5. **Performance test** critical paths

---

## 7. Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking changes | Medium | High | Extensive testing, feature flags |
| Performance regression | Low | Medium | Benchmark before/after |
| Increased complexity | Medium | Medium | Thorough documentation |
| Incomplete refactoring | High | Low | Incremental approach, version control |

---

## 8. Success Metrics

- **Code Duplication**: Reduce from ~40% to <10% in endpoints
- **Test Coverage**: Maintain ≥90%
- **Cyclomatic Complexity**: Reduce functions >15 to <10
- **Documentation**: 100% of public API documented
- **Performance**: <5% overhead from refactoring

---

## 9. References

- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [DRY Principle](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)
- [Refactoring Catalog](https://refactoring.com/catalog/)
- [Python Design Patterns](https://python-patterns.guide/)

---

## Conclusion

This refactoring guide provides a structured approach to improving the SDK's codebase. The recommendations are prioritized by impact and risk, allowing for incremental improvement without disrupting ongoing development.

**Recommended Next Steps**:
1. Review and discuss this guide with the team
2. Prioritize refactorings based on current project needs
3. Start with Phase 1 quick wins
4. Track progress using project management tools

**Estimated Total Effort**: 60-80 hours for complete implementation
**Recommended Timeline**: 8-12 weeks with 1-2 developers
