# String Analyzer Service

A RESTful API service built with Django and Django REST Framework that analyzes strings and stores their computed properties.

## Features

- Analyze strings and compute properties: length, palindrome check, unique characters, word count, SHA-256 hash, character frequency map
- Store analyzed strings in memory (data persists during server runtime)
- Retrieve specific strings by value
- Filter strings by various criteria (palindrome, length, word count, character presence)
- Natural language filtering for queries like "all single word palindromic strings"

## API Endpoints

### 1. Create/Analyze String
- **POST** `/api/strings`
- Request Body: `{"value": "string to analyze"}`
- Success: 201 Created with full string data
- Errors: 400 (missing value), 409 (duplicate), 422 (invalid type)

### 2. Get Specific String
- **GET** `/api/strings/{string_value}`
- Success: 200 OK with string data
- Error: 404 Not Found

### 3. Get All Strings with Filtering
- **GET** `/api/strings/?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a`
- Query Params: is_palindrome, min_length, max_length, word_count, contains_character
- Success: 200 OK with filtered data and count
- Error: 400 Bad Request for invalid params

### 4. Natural Language Filtering
- **GET** `/api/strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings`
- Supported queries: single word, palindromic, longer than X, containing letter Y
- Success: 200 OK with interpreted query and results
- Errors: 400 (missing query), 422 (conflicting filters)

### 5. Delete String
- **DELETE** `/api/strings/{string_value}`
- Success: 204 No Content
- Error: 404 Not Found

## Setup Instructions

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations (optional, since using in-memory storage): `python manage.py migrate`
6. Start the server: `python manage.py runserver`

## Dependencies

- Django==5.2.7
- djangorestframework==3.15.2
- asgiref==3.10.0
- sqlparse==0.5.3
- tzdata==2025.2

## Environment Variables

None required. The service uses in-memory storage, so no database configuration is needed.

## Testing

Use tools like Postman or curl to test the endpoints. Example:

```bash
# Create a string
curl -X POST http://127.0.0.1:8000/api/strings -H "Content-Type: application/json" -d '{"value": "hello world"}'

# Get all strings
curl http://127.0.0.1:8000/api/strings

# Get specific string
curl http://127.0.0.1:8000/api/strings/hello%20world

# Filter strings
curl "http://127.0.0.1:8000/api/strings/?is_palindrome=false"

# Natural language filter
curl "http://127.0.0.1:8000/api/strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings"

# Delete string
curl -X DELETE http://127.0.0.1:8000/api/strings/hello%20world
```

## Notes

- Data is stored in memory and will be lost when the server restarts.
- SHA-256 hash is used as the unique identifier for strings.
- Natural language parsing is basic and supports a limited set of query patterns.
- All string comparisons are case-insensitive for palindrome checks.
