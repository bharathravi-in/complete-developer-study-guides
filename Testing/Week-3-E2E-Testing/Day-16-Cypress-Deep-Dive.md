# Day 16: Cypress Deep Dive – Modern E2E Testing

## 📚 Topics to Cover (3-4 hours)

---

## 1. Cypress Setup

```bash
npm install --save-dev cypress @testing-library/cypress
npx cypress open  # Opens Cypress GUI
npx cypress run   # Headless CI mode
```

### cypress.config.ts

```typescript
import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:4200',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    retries: { runMode: 2, openMode: 0 },
    defaultCommandTimeout: 10000,
    setupNodeEvents(on, config) {
      // plugins
    },
    specPattern: 'cypress/e2e/**/*.cy.{js,ts}',
  },
});
```

---

## 2. Core Commands

```typescript
// Navigation
cy.visit('/login');
cy.visit('/users?page=1');
cy.go('back');
cy.reload();

// Querying
cy.get('[data-testid="submit"]');
cy.get('.btn-primary').first();
cy.get('ul li').eq(2);
cy.contains('Submit Order');
cy.get('form').find('input[name="email"]');

// Actions
cy.get('input').type('hello@test.com');
cy.get('input').clear().type('new value');
cy.get('button').click();
cy.get('button').dblclick();
cy.get('button').rightclick();
cy.get('select').select('Option 1');
cy.get('input[type="checkbox"]').check();
cy.get('input[type="checkbox"]').uncheck();
cy.get('.scrollable').scrollTo('bottom');
cy.get('.draggable').trigger('mousedown').trigger('mousemove', { clientX: 100 });

// Assertions
cy.get('.title').should('have.text', 'Welcome');
cy.get('.title').should('contain', 'Welcome');
cy.get('.title').should('be.visible');
cy.get('input').should('have.value', 'John');
cy.get('.error').should('not.exist');
cy.get('button').should('be.disabled');
cy.url().should('include', '/dashboard');
cy.get('.items').should('have.length', 5);
cy.get('.item').should('have.class', 'active');
cy.get('input').should('have.attr', 'placeholder', 'Enter name');
```

---

## 3. Common Test Patterns

### Login Flow

```typescript
describe('Authentication', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('should login with valid credentials', () => {
    cy.get('[data-testid="email"]').type('admin@test.com');
    cy.get('[data-testid="password"]').type('Admin123!');
    cy.get('[data-testid="login-btn"]').click();

    cy.url().should('include', '/dashboard');
    cy.get('[data-testid="welcome"]').should('contain', 'Welcome, Admin');
  });

  it('should show error for invalid password', () => {
    cy.get('[data-testid="email"]').type('admin@test.com');
    cy.get('[data-testid="password"]').type('wrong');
    cy.get('[data-testid="login-btn"]').click();

    cy.get('[data-testid="error"]').should('be.visible')
      .and('contain', 'Invalid credentials');
    cy.url().should('include', '/login');
  });
});
```

### CRUD Operations

```typescript
describe('Todo Management', () => {
  beforeEach(() => {
    cy.login('user@test.com', 'password'); // custom command
    cy.visit('/todos');
  });

  it('should create a new todo', () => {
    cy.get('[data-testid="new-todo"]').type('Buy groceries{enter}');
    cy.get('[data-testid="todo-list"]').should('contain', 'Buy groceries');
  });

  it('should mark todo as complete', () => {
    cy.get('[data-testid="todo-item"]').first()
      .find('[data-testid="toggle"]').click();
    cy.get('[data-testid="todo-item"]').first()
      .should('have.class', 'completed');
  });

  it('should delete a todo', () => {
    cy.get('[data-testid="todo-item"]').should('have.length', 3);
    cy.get('[data-testid="delete-btn"]').first().click();
    cy.get('[data-testid="todo-item"]').should('have.length', 2);
  });
});
```

---

## 4. API Interception

```typescript
// Stub API responses
cy.intercept('GET', '/api/users', {
  statusCode: 200,
  body: [{ id: 1, name: 'John' }, { id: 2, name: 'Jane' }],
}).as('getUsers');

cy.visit('/users');
cy.wait('@getUsers');
cy.get('.user-card').should('have.length', 2);

// Simulate error
cy.intercept('GET', '/api/users', {
  statusCode: 500,
  body: { error: 'Server Error' },
}).as('getUsersError');

cy.visit('/users');
cy.wait('@getUsersError');
cy.get('.error-message').should('contain', 'Failed to load');

// Spy on requests (without modifying)
cy.intercept('POST', '/api/orders').as('createOrder');
// ... perform actions
cy.wait('@createOrder').then((interception) => {
  expect(interception.request.body).to.have.property('amount', 99.99);
  expect(interception.response.statusCode).to.eq(201);
});

// Delay response
cy.intercept('GET', '/api/data', (req) => {
  req.reply({ delay: 2000, body: { data: [] } });
});
```

---

## 5. Custom Commands

```typescript
// cypress/support/commands.ts
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.session([email, password], () => {
    cy.visit('/login');
    cy.get('[data-testid="email"]').type(email);
    cy.get('[data-testid="password"]').type(password);
    cy.get('[data-testid="submit"]').click();
    cy.url().should('include', '/dashboard');
  });
});

Cypress.Commands.add('apiLogin', (email: string, password: string) => {
  cy.request('POST', '/api/auth/login', { email, password })
    .then((response) => {
      window.localStorage.setItem('token', response.body.token);
    });
});

// Usage
cy.login('admin@test.com', 'password');
// or faster:
cy.apiLogin('admin@test.com', 'password');
```

---

## 6. Page Object Model in Cypress

```typescript
// cypress/pages/LoginPage.ts
export class LoginPage {
  visit() {
    cy.visit('/login');
    return this;
  }

  getEmailInput() { return cy.get('[data-testid="email"]'); }
  getPasswordInput() { return cy.get('[data-testid="password"]'); }
  getSubmitButton() { return cy.get('[data-testid="submit"]'); }
  getErrorMessage() { return cy.get('[data-testid="error"]'); }

  login(email: string, password: string) {
    this.getEmailInput().type(email);
    this.getPasswordInput().type(password);
    this.getSubmitButton().click();
    return this;
  }
}

// Test using Page Object
const loginPage = new LoginPage();

describe('Login', () => {
  it('should login successfully', () => {
    loginPage.visit().login('user@test.com', 'password');
    cy.url().should('include', '/dashboard');
  });

  it('should show error', () => {
    loginPage.visit().login('bad@test.com', 'wrong');
    loginPage.getErrorMessage().should('be.visible');
  });
});
```

---

## 7. Visual Testing

```typescript
// With Percy
import '@percy/cypress';

it('should match visual snapshot', () => {
  cy.visit('/dashboard');
  cy.percySnapshot('Dashboard - Default View');

  cy.get('[data-testid="dark-mode"]').click();
  cy.percySnapshot('Dashboard - Dark Mode');
});
```

---

## 🎯 Interview Questions

### Q1: What makes Cypress different from Selenium?
**A:** Cypress runs in the same event loop as the app (not over WebDriver protocol), giving it automatic waiting, time-travel debugging, network stubbing, and real-time reloads. It's faster, more reliable, but currently limited to Chromium, Firefox, and Edge (no Safari).

### Q2: How do you handle flaky tests in Cypress?
**A:** Use `cy.intercept()` to control network (no real API flakiness), proper `should()` assertions (auto-retry), `cy.session()` for auth caching, avoid `cy.wait(ms)` in favor of waiting on aliases, increase `defaultCommandTimeout` if needed.

### Q3: How do you test file downloads in Cypress?
**A:** Use `cy.readFile()` to verify downloaded files, intercept download requests, or use the `cypress-downloadfile` plugin. Configure `downloadsFolder` in config and verify file content after download action.

---

## 📝 Practice Exercises

1. Write E2E tests for a complete CRUD application
2. Implement network stubbing for error and loading states
3. Create custom commands for authentication and common actions
4. Set up visual regression testing with Percy or Applitools
