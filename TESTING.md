# Testing Guide

This document provides comprehensive guidance for running tests in the CoffeeStudio platform.

## Backend Tests

### Prerequisites

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running Tests

**Run all tests:**
```bash
cd backend
pytest tests/ -v
```

**Run with coverage:**
```bash
cd backend
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

The HTML coverage report will be generated in `backend/htmlcov/index.html`.

**Run specific test file:**
```bash
pytest tests/test_cooperatives.py -v
```

**Run specific test:**
```bash
pytest tests/test_cooperatives.py::test_create_cooperative -v
```

**Run tests matching a pattern:**
```bash
pytest tests/ -k "auth" -v
```

### Test Structure

The backend test suite includes:

- **`conftest.py`** - Shared fixtures and test configuration
  - Test database setup (SQLite in-memory)
  - Test client with dependency overrides
  - User fixtures for different roles (admin, analyst, viewer)
  - Authentication header fixtures

- **`test_cooperatives.py`** - Cooperative CRUD operations (14 tests)
  - Create, read, update, delete operations
  - Input validation
  - Authorization checks
  - Error handling
  - Audit logging integration

- **`test_roasters.py`** - Roaster CRUD operations (14 tests)
  - Create, read, update, delete operations
  - Role-based access control
  - Error handling

- **`test_auth.py`** - Authentication and authorization (14 tests)
  - Login success and failure scenarios
  - Token validation
  - Protected route access
  - Role-based restrictions
  - Inactive user handling

- **`test_middleware.py`** - Security middleware (8 tests)
  - Security headers validation
  - SQL injection detection
  - XSS attack prevention
  - Rate limiting
  - CORS configuration
  - Input validation

- **`test_export.py`** - Data export functionality (7 tests)
  - CSV export for cooperatives and roasters
  - Authorization checks
  - Data formatting validation

### Test Database

Tests use an in-memory SQLite database that is:
- Created fresh for each test
- Automatically cleaned up after each test
- Compatible with PostgreSQL models via SQLAlchemy

### Coverage Goals

- **Current**: 55 tests covering core CRUD operations, auth, security, and data export
- **Coverage**: 58% (exceeds target of 57%)
- **Target**: ≥80% code coverage for production readiness

### Enterprise Validation

Run the comprehensive enterprise validation script:

```bash
./scripts/enterprise_validation.sh
```

This script runs:
- Ruff linting
- Black code formatting check
- Mypy type checking
- Full test suite with coverage
- Security middleware validation
- Rate limiting tests
- Audit logging tests
- Configuration validation
- Documentation completeness check

### Writing New Tests

Example test structure:

```python
def test_create_resource(client, auth_headers, db):
    """Test creating a new resource."""
    payload = {
        "name": "Test Resource",
        "value": 100
    }
    
    response = client.post("/api/resources", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Resource"
```

## Frontend Tests

### Prerequisites

```bash
cd frontend
npm install
```

### Running Tests

**Run all tests:**
```bash
cd frontend
npm run test
```

**Run with UI:**
```bash
npm run test:ui
```

**Generate coverage report:**
```bash
npm run test:coverage
```

### Test Structure

Frontend tests use:
- **Vitest** - Fast test runner for Vite projects
- **React Testing Library** - Component testing utilities
- **@testing-library/jest-dom** - Custom matchers

## Continuous Integration

All tests run automatically on:
- Every push to any branch
- Every pull request
- Before deployment to staging/production

### CI Pipeline

1. **Backend Tests** - Linting, type checking, unit tests
2. **Frontend Tests** - Linting, build, unit tests
3. **Security Scans** - Semgrep (SAST) and Trivy (vulnerability scanning)
4. **Docker Builds** - Verify containers build successfully

### Local CI Simulation

Test your changes locally before pushing:

```bash
# Backend
cd backend
ruff check .
mypy --config-file ../mypy.ini app
pytest tests/ -v

# Frontend
cd frontend
npm run lint
npm run build
npm run test
```

## Troubleshooting

### Backend Tests

**Issue: Tests fail with database errors**
```
Solution: Ensure you're using the test environment. Tests use SQLite in-memory database.
```

**Issue: Import errors**
```
Solution: Make sure you're in the backend directory and have installed requirements-dev.txt
```

**Issue: Rate limit errors in auth tests**
```
Solution: Tests automatically reset rate limiter state. This should not occur.
```

### Frontend Tests

**Issue: Module not found errors**
```
Solution: Run npm install to ensure all dependencies are installed
```

**Issue: Component tests fail**
```
Solution: Check that @testing-library packages are installed
```

## Best Practices

1. **Write descriptive test names** - Test names should clearly describe what is being tested
2. **Test one thing per test** - Keep tests focused and simple
3. **Use fixtures for common setup** - Avoid repetitive setup code
4. **Test edge cases** - Don't just test the happy path
5. **Keep tests fast** - Use in-memory databases and mocks
6. **Clean up after tests** - Use fixtures to ensure proper cleanup
7. **Test error conditions** - Verify proper error handling

## Performance

- Backend tests: ~5 seconds for 55 tests
- Coverage: 58%
- All tests use in-memory SQLite database for speed
- Frontend tests: (to be measured after implementation)

## Code Coverage

View coverage reports:

**Backend:**
```bash
cd backend
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

**Frontend:**
```bash
cd frontend
npm run test:coverage
open coverage/index.html
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
