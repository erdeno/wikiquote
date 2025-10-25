#!/bin/bash

echo "Testing Authentication System"
echo "=============================="

API_URL="http://localhost:8000/api/v1"

# Test Registration
echo -e "\n1. Testing Registration..."
curl -X POST $API_URL/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }' | python -m json.tool

# Test Login
echo -e "\n2. Testing Login..."
LOGIN_RESPONSE=$(curl -s -X POST $API_URL/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }')

echo $LOGIN_RESPONSE | python3 -m json.tool

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "Login failed!"
    exit 1
fi

echo "Token: $TOKEN"

# Test Profile
echo -e "\n3. Testing Profile..."
curl -X GET $API_URL/auth/profile/ \
  -H "Authorization: Token $TOKEN" | python3 -m json.tool

# Test Logout
echo -e "\n4. Testing Logout..."
curl -X POST $API_URL/auth/logout/ \
  -H "Authorization: Token $TOKEN" | python3 -m json.tool

echo -e "\n=============================="
echo "Tests completed!"
