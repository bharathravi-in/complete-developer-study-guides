# Testing Cheatsheets

## Jest Quick Reference

```javascript
// Matchers
expect(x).toBe(y)              // strict equality
expect(x).toEqual(y)           // deep equality
expect(x).toBeTruthy()         // truthy check
expect(x).toBeNull()           // null check
expect(x).toBeDefined()        // not undefined
expect(x).toContain(item)      // array/string contains
expect(x).toMatch(/regex/)     // regex match
expect(x).toHaveLength(n)      // length check
expect(fn).toThrow()           // throws error
expect(x).toBeGreaterThan(y)   // number comparison
expect(x).toBeCloseTo(y)       // floating point

// Mocks
const fn = jest.fn()                           // create mock
fn.mockReturnValue(42)                         // return value
fn.mockResolvedValue(data)                     // async return
fn.mockImplementation((a) => a * 2)            // custom impl
jest.spyOn(obj, 'method')                      // spy on method
jest.mock('./module')                          // mock module

// Assertions on mocks
expect(fn).toHaveBeenCalled()
expect(fn).toHaveBeenCalledTimes(n)
expect(fn).toHaveBeenCalledWith(args)

// Async
await expect(promise).resolves.toBe(val)
await expect(promise).rejects.toThrow()

// Timers
jest.useFakeTimers()
jest.advanceTimersByTime(1000)
jest.useRealTimers()
```

## Cypress Quick Reference

```javascript
// Navigation & Querying
cy.visit('/path')
cy.get('[data-testid="id"]')
cy.contains('text')
cy.get('form').find('input')

// Actions
cy.get('input').type('text')
cy.get('button').click()
cy.get('select').select('opt')
cy.get('input').clear()

// Assertions
cy.get(el).should('be.visible')
cy.get(el).should('have.text', 'x')
cy.get(el).should('contain', 'x')
cy.get(el).should('not.exist')
cy.url().should('include', '/path')

// Network
cy.intercept('GET', '/api/*', { body: [] }).as('alias')
cy.wait('@alias')
```

## Playwright Quick Reference

```typescript
// Locators
page.getByRole('button', { name: 'Submit' })
page.getByLabel('Email')
page.getByText('Welcome')
page.getByTestId('element')

// Actions
await locator.click()
await locator.fill('text')
await locator.check()
await locator.selectOption('value')

// Assertions
await expect(locator).toBeVisible()
await expect(locator).toHaveText('text')
await expect(page).toHaveURL('/path')
await expect(locator).toHaveCount(n)

// Network
await page.route('/api/*', route => route.fulfill({ body: '[]' }))
```

## Pytest Quick Reference

```python
# Assertions
assert x == y
assert x in collection
with pytest.raises(ValueError): func()
assert x == pytest.approx(0.3)

# Fixtures
@pytest.fixture
def data(): return {"key": "value"}

@pytest.fixture(scope="session")
def db(): yield setup_db(); teardown()

# Parametrize
@pytest.mark.parametrize("input,expected", [(1,1), (2,4)])
def test_square(input, expected): assert input**2 == expected

# Markers
@pytest.mark.skip(reason="WIP")
@pytest.mark.skipif(condition)
@pytest.mark.xfail
@pytest.mark.slow

# Mock
@patch('module.function')
def test_x(mock_fn): mock_fn.return_value = 42
```
