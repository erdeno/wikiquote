#!/bin/bash

echo "========================================"
echo "Running Test Suite"
echo "========================================"

cd backend

# Run all tests with coverage
echo -e "\n1. Running all tests with coverage..."
pytest -v --cov=. --cov-report=html --cov-report=term-missing

# Run specific test categories
echo -e "\n2. Running unit tests only..."
pytest -v -m unit

echo -e "\n3. Running API tests only..."
pytest -m api

echo -e "\n4. Running voice service tests..."
pytest -m voice

# Generate coverage report
echo -e "\n5. Coverage Summary:"
coverage report

echo -e "\n========================================"
echo "Tests Complete!"
echo "========================================"
echo "HTML coverage report: backend/htmlcov/index.html"