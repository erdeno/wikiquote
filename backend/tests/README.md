# Test Suite Documentation

## Overview

Comprehensive test suite for the "Which Quote?" NLP capstone project with full coverage of:
- User authentication
- Voice services (ASR, Speaker ID, TTS)
- API endpoints
- Database models
- Integration workflows

## Running Tests

### Run All Tests
```bash
./run_tests.sh
```

### Run Specific Categories
```bash
# Unit tests only
pytest -m unit

# API tests only
pytest -m api

# Voice service tests
pytest -m voice

# Integration tests
pytest -m integration

# Slow tests
pytest -m slow
```

### Run Specific Test Files
```bash
pytest tests/accounts/test_models.py
pytest tests/voice/test_views.py
pytest tests/services/test_whisper.py
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html --cov-report=term-missing
```

### View Coverage Report
```bash
# Open in browser
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Structure
```
tests/
├── accounts/
│   ├── test_models.py       # User & Profile model tests
│   ├── test_views.py        # Auth endpoint tests
│   └── test_serializers.py  # Serializer tests
├── quotes/
│   ├── test_models.py       # Quote model tests
│   └── test_views.py        # Quote API tests
├── voice/
│   ├── test_views.py        # Voice endpoint tests
│   └── test_chatbot.py      # Chatbot logic tests
├── services/
│   ├── test_whisper.py      # ASR tests
│   ├── test_speaker_id.py   # Speaker recognition tests
│   └── test_tts.py          # TTS tests
├── test_integration.py      # End-to-end tests
├── test_performance.py      # Performance tests
├── factories.py             # Test data factories
└── README.md               # This file
```

## Coverage Goals

- **Target**: 90%+ coverage
- **Current**: Run `coverage report` to check

### Areas Covered

✅ User registration/login/logout
✅ Profile management
✅ Voice registration
✅ Speaker identification
✅ ASR transcription
✅ TTS synthesis
✅ API authentication
✅ Error handling

### Exclusions

- Migration files
- Test files themselves
- Third-party packages
- Development utilities

## Writing New Tests

### Test Naming Convention
```python
def test_<feature>_<scenario>():
    """Brief description"""
    # Arrange
    # Act
    # Assert
```

### Use Fixtures
```python
def test_with_authenticated_user(authenticated_client):
    response = authenticated_client.get('/api/v1/auth/profile/')
    assert response.status_code == 200
```

### Use Markers
```python
@pytest.mark.unit
@pytest.mark.django_db
def test_model_creation():
    ...
```

### Mock External Services
```python
def test_with_mock(mock_whisper, mock_tts):
    # Tests run faster and don't depend on external services
    ...
```

## Common Fixtures

### `api_client`
Unauthenticated API client

### `authenticated_client`
API client with authentication token

### `sample_audio_bytes`
Sample audio data for testing

### `mock_whisper`
Mocked Whisper ASR service

### `mock_speechbrain`
Mocked SpeechBrain speaker recognition

### `mock_tts`
Mocked Coqui TTS service

## Continuous Integration

Add to your CI pipeline:
```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          file: ./backend/coverage.xml
```

## Troubleshooting

### Tests fail with "no module named X"
```bash
# Make sure you're in the backend directory
cd backend
pytest
```

### Mock not working
```bash
# Check fixture spelling and imports
# Ensure mock is properly configured in conftest.py
```

### Database errors
```bash
# Tests should use test database automatically
# If issues persist, try:
python manage.py migrate --settings=config.test_settings
```

## Best Practices

1. **Test behavior, not implementation**
2. **Keep tests independent** - no test should depend on another
3. **Use descriptive names** - test names should explain what they test
4. **Mock external services** - tests should be fast and reliable
5. **Test edge cases** - not just happy paths
6. **Keep tests simple** - one concept per test
7. **Update tests with code** - tests are documentation

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Django Testing](https://docs.djangoproject.com/en/4.2/topics/testing/)
- [Factory Boy](https://factoryboy.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)