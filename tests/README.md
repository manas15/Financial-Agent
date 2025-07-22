# Tests Directory

This directory contains all test files for the Financial Agent application.

## Test Structure

### Backend Tests
- **`test_backend.py`** - Core backend API endpoint tests
- **`test_simple_backend.py`** - Simple backend functionality tests
- **`test_full_system.py`** - Complete system integration tests
- **`test_db_connection.py`** - Database connection and operations tests
- **`test_without_db.py`** - Tests that run without database dependency

### Data & Services Tests
- **`test_data_collection.py`** - Data collection and processing tests
- **`test_data_only.py`** - Pure data manipulation tests
- **`test_claude_api.py`** - Claude AI API integration tests

### Basic Tests
- **`test_simple.py`** - Basic functionality tests

## Running Tests

### Prerequisites
Make sure you have the required dependencies installed:
```bash
pip install pytest pytest-asyncio httpx
```

### Run All Tests
```bash
# From project root
python -m pytest tests/

# With verbose output
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=src
```

### Run Specific Test Categories

#### Backend Tests
```bash
python -m pytest tests/test_backend.py
python -m pytest tests/test_simple_backend.py
python -m pytest tests/test_full_system.py
```

#### Database Tests
```bash
python -m pytest tests/test_db_connection.py
```

#### API Integration Tests
```bash
python -m pytest tests/test_claude_api.py
```

#### Data Tests
```bash
python -m pytest tests/test_data_collection.py
python -m pytest tests/test_data_only.py
```

#### Tests Without Dependencies
```bash
python -m pytest tests/test_without_db.py
python -m pytest tests/test_simple.py
```

### Environment Setup for Tests

Make sure to set up your environment variables:
```bash
export ANTHROPIC_API_KEY="your_claude_api_key"
export DATABASE_URL="sqlite:///./test_financial_agent.db"
```

## Test Categories

### Unit Tests
- Individual component testing
- No external dependencies
- Fast execution

### Integration Tests
- Multi-component testing
- Database integration
- API integration
- Yahoo Finance MCP service testing

### System Tests
- End-to-end functionality
- Full application workflow
- Real API calls (with proper mocking)

## Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Use mocks for external APIs in unit tests
3. **Cleanup**: Clean up test data after each test
4. **Naming**: Use descriptive test names that explain what is being tested
5. **Documentation**: Add docstrings to complex test scenarios

## Continuous Integration

These tests are designed to run in CI/CD environments. Make sure to:
- Set appropriate environment variables
- Use test databases
- Mock external API calls when appropriate
- Handle timeouts gracefully