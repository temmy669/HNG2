import re
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .utils import compute_properties

# In-memory storage: dict with sha256_hash as key
strings_storage = {}


class StringListCreateView(APIView):
    def post(self, request):
        value = request.data.get('value')
        if not value:
            return Response({'error': 'Missing "value" field'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(value, str):
            return Response({'error': '"value" must be a string'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        properties = compute_properties(value)
        sha256_hash = properties['sha256_hash']
        if sha256_hash in strings_storage:
            return Response({'error': 'String already exists'}, status=status.HTTP_409_CONFLICT)
        
        entry = {
            'id': sha256_hash,
            'value': value,
            'properties': properties,
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }
        strings_storage[sha256_hash] = entry
        return Response(entry, status=status.HTTP_201_CREATED)

    def get(self, request):
        # Filtering logic
        filters = {}
        if 'is_palindrome' in request.query_params:
            filters['is_palindrome'] = request.query_params['is_palindrome'].lower() == 'true'
        if 'min_length' in request.query_params:
            try:
                filters['min_length'] = int(request.query_params['min_length'])
            except ValueError:
                return Response({'error': 'Invalid min_length'}, status=status.HTTP_400_BAD_REQUEST)
        if 'max_length' in request.query_params:
            try:
                filters['max_length'] = int(request.query_params['max_length'])
            except ValueError:
                return Response({'error': 'Invalid max_length'}, status=status.HTTP_400_BAD_REQUEST)
        if 'word_count' in request.query_params:
            try:
                filters['word_count'] = int(request.query_params['word_count'])
            except ValueError:
                return Response({'error': 'Invalid word_count'}, status=status.HTTP_400_BAD_REQUEST)
        if 'contains_character' in request.query_params:
            char = request.query_params['contains_character']
            if len(char) != 1:
                return Response({'error': 'contains_character must be a single character'}, status=status.HTTP_400_BAD_REQUEST)
            filters['contains_character'] = char

        # Apply filters
        data = []
        for entry in strings_storage.values():
            props = entry['properties']
            if 'is_palindrome' in filters and props['is_palindrome'] != filters['is_palindrome']:
                continue
            if 'min_length' in filters and props['length'] < filters['min_length']:
                continue
            if 'max_length' in filters and props['length'] > filters['max_length']:
                continue
            if 'word_count' in filters and props['word_count'] != filters['word_count']:
                continue
            if 'contains_character' in filters and filters['contains_character'] not in entry['value']:
                continue
            data.append(entry)

        return Response({
            'data': data,
            'count': len(data),
            'filters_applied': filters
        })

class StringDetailView(APIView):
    def get(self, request, string_value):
        # Find by value, but since id is hash, we need to search
        for entry in strings_storage.values():
            if entry['value'] == string_value:
                return Response(entry)
        raise Http404

    def delete(self, request, string_value):
        for key, entry in strings_storage.items():
            if entry['value'] == string_value:
                del strings_storage[key]
                return Response(status=status.HTTP_204_NO_CONTENT)
        raise Http404

class StringNaturalLanguageFilterView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        if not query:
            return Response({'error': 'Missing query parameter'}, status=status.HTTP_400_BAD_REQUEST)

        parsed_filters = {}
        original = query.lower()

        # Simple parsing for supported queries
        if 'single word' in original or 'word_count=1' in original:
            parsed_filters['word_count'] = 1
        if 'palindromic' in original or 'is_palindrome=true' in original:
            parsed_filters['is_palindrome'] = True
        if 'longer than' in original:
            match = re.search(r'longer than (\d+) characters?', original)
            if match:
                parsed_filters['min_length'] = int(match.group(1)) + 1
        if 'containing the letter' in original:
            match = re.search(r'containing the letter (\w)', original)
            if match:
                parsed_filters['contains_character'] = match.group(1)
        if 'containing' in original and 'first vowel' in original:
            parsed_filters['contains_character'] = 'a'  # heuristic

        # Check for conflicts (none expected in simple parsing)

        # Apply filters
        data = []
        for entry in strings_storage.values():
            props = entry['properties']
            match = True
            if 'word_count' in parsed_filters and props['word_count'] != parsed_filters['word_count']:
                match = False
            if 'is_palindrome' in parsed_filters and props['is_palindrome'] != parsed_filters['is_palindrome']:
                match = False
            if 'min_length' in parsed_filters and props['length'] < parsed_filters['min_length']:
                match = False
            if 'contains_character' in parsed_filters and parsed_filters['contains_character'] not in entry['value']:
                match = False
            if match:
                data.append(entry)

        return Response({
            'data': data,
            'count': len(data),
            'interpreted_query': {
                'original': query,
                'parsed_filters': parsed_filters
            }
        })
