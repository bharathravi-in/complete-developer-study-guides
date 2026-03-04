# Testing Interview Questions – Comprehensive Q&A

## 📚 100+ Interview Questions for Senior Engineers

---

## Unit Testing

### Q1: What is the testing pyramid and why is it important?
**A:** The testing pyramid suggests many fast unit tests at the base, fewer integration tests in the middle, and minimal E2E tests at the top. It optimizes for fast feedback, lower maintenance cost, and reliable test suites. Modern alternatives like the "testing trophy" emphasize integration tests for best ROI.

### Q2: TDD vs BDD — When to use each?
**A:** TDD: Developer-focused, test-first for code correctness, ideal for business logic and algorithms. BDD: Business-stakeholder collaboration, Given-When-Then format, ideal for acceptance criteria. Use TDD for implementation details, BDD for feature specifications.

### Q3: What makes a test "good"?
**A:** FIRST principles: Fast, Independent, Repeatable, Self-validating, Timely. Also: tests behavior (not implementation), has clear naming, tests one scenario, is deterministic, doesn't depend on other tests.

### Q4: Explain mocks vs stubs vs fakes vs spies
**A:** **Stub**: Returns canned data. **Mock**: Verifies interactions/expectations. **Spy**: Wraps real implementation, records calls. **Fake**: Simplified working implementation (in-memory DB). Modern frameworks blur these distinctions.

### Q5: What is over-mocking?
**A:** Mocking too many dependencies, making tests pass regardless of real behavior. Signs: tests don't catch bugs, tests break when refactoring internal details, adding mocks is more code than the feature. Fix: prefer integration tests, mock only external boundaries.

---

## JavaScript/TypeScript Testing

### Q6: Jest vs Jasmine — key differences?
**A:** Jest: Zero-config, built-in mocking (`jest.mock()`), snapshot testing, faster (Node.js), code coverage built-in. Jasmine: Angular default, browser-based via Karma, `createSpyObj`, BDD syntax. Jest is better for React/Node, Jasmine for Angular (but Angular 16+ supports Jest).

### Q7: How does `jest.mock()` work under the hood?
**A:** Jest hoists `jest.mock()` to file top via babel transform. It replaces module exports in the module registry with mock implementations. All imports in the test file get the mocked version. `jest.requireActual()` bypasses this.

### Q8: Explain snapshot testing — when is it useful?
**A:** Captures component output and compares to stored snapshot. Good for: UI regression detection, serializable output verification. Bad for: frequently changing components, testing behavior. Update with `--updateSnapshot`. Prefer inline snapshots for small outputs.

### Q9: How do you test async code in Jest?
**A:** Four approaches: (1) Return promise, (2) async/await (preferred), (3) done callback, (4) resolves/rejects matchers. Always handle both success and error paths. Use `waitFor` with React Testing Library.

### Q10: How do you handle flaky tests?
**A:** Root causes: timing issues, shared state, external dependencies, random data. Solutions: deterministic test data, proper setup/teardown, mock external services, avoid `sleep()` in favor of polling/waiting, run tests in isolation.

---

## React Testing

### Q11: Why React Testing Library over Enzyme?
**A:** RTL tests behavior (what users see/do), Enzyme tests internals (state, props, instances). RTL prevents accessing component internals, forcing better tests. RTL is React team's recommended approach. Enzyme doesn't support React 18+.

### Q12: What query priority should you use in RTL?
**A:** `getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByDisplayValue` > `getByAltText` > `getByTitle` > `getByTestId`. Role-based queries are most maintainable and accessible.

### Q13: How do you test hooks with RTL?
**A:** Use `renderHook` from `@testing-library/react`. Wrap in `act()` for state updates. Provide context via wrapper option. Test return values and side effects, not hook internals.

### Q14: How do you test components with Redux?
**A:** Create a custom `renderWithProviders` that wraps component with `<Provider>`. Pass `preloadedState` for specific scenarios. Assert against store state changes and UI updates. Prefer testing user interactions over dispatched actions.

---

## Angular Testing

### Q15: Explain TestBed in Angular testing
**A:** TestBed configures a testing module (like `@NgModule`). It declares components, provides services (with mocks), imports modules. `compileComponents()` compiles templates. `createComponent()` creates component fixtures for testing.

### Q16: fakeAsync vs waitForAsync?
**A:** `fakeAsync`: Synchronous simulation of time, use `tick()` to advance. Better control, preferred for most tests. `waitForAsync`: Real async zone, waits for microtasks/macrotasks. Use when `fakeAsync` can't handle specific async patterns.

### Q17: How do you test HTTP calls in Angular?
**A:** Use `HttpClientTestingModule` + `HttpTestingController`. Inject controller, make service call, use `expectOne()` to assert request, `flush()` to provide mock response. Always call `verify()` in afterEach.

---

## E2E Testing

### Q18: Cypress vs Playwright — when to use each?
**A:** Cypress: Simpler API, great DevX, component testing support, single-browser focus. Playwright: Cross-browser (including Safari), multi-tab, mobile emulation, built-in parallelism, multiple language support. Choose Playwright for cross-browser, Cypress for simplicity.

### Q19: How do you handle authentication in E2E tests?
**A:** Don't login through UI for every test. Cypress: `cy.session()` or programmatic login via API. Playwright: `storageState` files. Both save cookies/localStorage and reuse across tests.

### Q20: What is the Page Object Model?
**A:** Design pattern that encapsulates page interactions in classes. Each page/component has a class with locators and action methods. Tests use page objects instead of raw selectors. Benefits: DRY, maintainable, readable tests.

### Q21: How do you handle flaky E2E tests?
**A:** Root causes: network timing, animations, dynamic content. Solutions: Mock APIs (`intercept`/`route`), disable animations, use proper waits (not `sleep`), stable selectors (`data-testid`), retry logic, run in consistent environment.

---

## Performance Testing

### Q22: What are Core Web Vitals?
**A:** Google's user experience metrics: LCP (loading speed, ≤2.5s), FID/INP (interactivity, ≤100ms/200ms), CLS (visual stability, ≤0.1). They affect SEO ranking and measure real user experience.

### Q23: How do you performance test an API?
**A:** Use load testing tools (k6, Artillery, Locust). Key metrics: p50/p95/p99 response times, throughput (req/s), error rate. Test patterns: ramp-up, steady state, spike, endurance. Set SLA thresholds and fail CI if exceeded.

### Q24: How do you detect memory leaks?
**A:** DevTools heap snapshots (before/after), comparison for growing objects. Common causes: unremoved event listeners, unsubscribed observables, closures, detached DOM. Fix: cleanup in lifecycle hooks, WeakRef/WeakMap, proper RxJS unsubscribe patterns.

---

## Testing Architecture

### Q25: How do you test microservices?
**A:** Unit tests per service, contract tests between services (Pact), integration tests with real dependencies (Docker Compose), E2E tests for critical flows. Use consumer-driven contracts to prevent breaking changes.

### Q26: What is contract testing?
**A:** Verifies API contracts between consumer and provider without integration testing. Consumer defines expected interactions, provider verifies compliance. Tools: Pact, Spring Cloud Contract. Catches breaking changes early.

### Q27: How do you test error handling?
**A:** Test every error path: network errors, validation errors, auth errors, timeout errors, unexpected data. Verify error messages, fallback behavior, retry logic, error boundaries (React), and error interceptors (Angular).

### Q28: What is mutation testing?
**A:** Modifies source code (mutations) and checks if tests catch changes. Survived mutations = weak tests. Measures test quality beyond coverage. Tools: Stryker (JS), mutmut (Python). Use for critical business logic.

---

## CI/CD & Testing Strategy

### Q29: How do you set up testing in CI/CD?
**A:** Run unit tests on every commit (fast gate). Integration tests on PR. E2E tests before deployment. Coverage gates (80%+). Parallel execution for speed. Artifact storage for reports. Flaky test quarantine.

### Q30: What's your testing strategy for a new project?
**A:** (1) Set up testing infrastructure first (CI, coverage, linting). (2) TDD for business logic. (3) Integration tests for API endpoints. (4) Component tests for UI. (5) E2E for critical user flows. (6) Performance tests for SLA validation. (7) Monitor code coverage trends.
