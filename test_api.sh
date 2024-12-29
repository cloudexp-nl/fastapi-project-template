#!/bin/bash

# Set base URL
BASE_URL="http://localhost:8000"
API_URL="$BASE_URL/api/v1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is not installed. Please install it first:${NC}"
    echo "brew install jq # for macOS"
    echo "sudo apt-get install jq # for Ubuntu/Debian"
    exit 1
fi

# Check if API is running
if ! curl -s "$BASE_URL" > /dev/null; then
    echo -e "${RED}Error: API is not running at $BASE_URL${NC}"
    echo "Please start the API server first"
    exit 1
fi

# Function to handle API errors
handle_response() {
    local response=$1
    local action=$2
    
    if [[ $(echo "$response" | jq -r 'if type=="object" then "true" else "false" end') == "true" ]]; then
        echo -e "${GREEN}✓ $action successful${NC}"
        echo "$response" | jq '.'
    else
        echo -e "${RED}✗ $action failed${NC}"
        echo "$response"
        exit 1
    fi
}

echo "Starting API tests..."

# Register user
echo -e "\n1. Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
-H "Content-Type: application/json" \
-d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test123!@#"
}')
handle_response "$REGISTER_RESPONSE" "User registration"

# Get token
echo -e "\n2. Getting token..."
TOKEN_RESPONSE=$(curl -s -X POST "$API_URL/auth/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=testuser&password=Test123!@#")

if ! TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token'); then
    echo -e "${RED}Failed to get token${NC}"
    echo "$TOKEN_RESPONSE" | jq '.'
    exit 1
fi
echo -e "${GREEN}✓ Token received:${NC} ${TOKEN:0:20}..."

# Create multiple posts
echo -e "\n3. Creating posts..."
for i in {1..3}; do
    echo -e "\nCreating post $i..."
    RESPONSE=$(curl -s -X POST "$API_URL/posts/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"title\": \"Test Post $i\",
        \"content\": \"This is test post content $i\"
    }")
    handle_response "$RESPONSE" "Post $i creation"
done

# Get posts with pagination
echo -e "\n4. Testing pagination..."
echo -e "\nFetching page 1 (size 2):"
PAGE1_RESPONSE=$(curl -s "$API_URL/posts/?page=1&size=2")
handle_response "$PAGE1_RESPONSE" "Page 1 fetch"

echo -e "\nFetching page 2 (size 2):"
PAGE2_RESPONSE=$(curl -s "$API_URL/posts/?page=2&size=2")
handle_response "$PAGE2_RESPONSE" "Page 2 fetch"

# Get specific post
echo -e "\n5. Getting specific post..."
POST_RESPONSE=$(curl -s "$API_URL/posts/1")
handle_response "$POST_RESPONSE" "Single post fetch"

echo -e "\n${GREEN}All tests completed successfully!${NC}" 