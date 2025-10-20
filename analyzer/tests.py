import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .views import strings_storage, compute_properties


class StringAnalyzerAPITestCase(APITestCase):
    def setUp(self):
        # Clear storage before each test
        strings_storage.clear()

    def test_compute_properties(self):
        """Test the compute_properties function."""
        value = "hello world"
        props = compute_properties(value)
        self.assertEqual(props['length'], 11)
        self.assertFalse(props['is_palindrome'])
        self.assertEqual(props['unique_characters'], 8)
        self.assertEqual(props['word_count'], 2)
        self.assertEqual(props['character_frequency_map']['l'], 3)

        # Test palindrome
        palindrome_props = compute_properties("radar")
        self.assertTrue(palindrome_props['is_palindrome'])

        # Test single word
        single_word_props = compute_properties("hello")
        self.assertEqual(single_word_props['word_count'], 1)

    def test_post_string_create_success(self):
        """Test successful string creation."""
        url = reverse('string-list-create')
        data = {'value': 'hello world'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['value'], 'hello world')
        self.assertIn('properties', response.data)
        self.assertIn('created_at', response.data)

    def test_post_string_missing_value(self):
        """Test POST with missing value field."""
        url = reverse('string-list-create')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_post_string_invalid_type(self):
        """Test POST with non-string value."""
        url = reverse('string-list-create')
        data = {'value': 123}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('error', response.data)

    def test_post_string_duplicate(self):
        """Test POST with duplicate string."""
        url = reverse('string-list-create')
        data = {'value': 'hello world'}
        self.client.post(url, data, format='json')  # Create first
        response = self.client.post(url, data, format='json')  # Try duplicate
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('error', response.data)

    def test_get_string_detail_success(self):
        """Test successful retrieval of specific string."""
        # First create a string
        url = reverse('string-list-create')
        data = {'value': 'hello world'}
        self.client.post(url, data, format='json')

        # Then retrieve it
        url = reverse('string-detail', kwargs={'string_value': 'hello world'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'hello world')

    def test_get_string_detail_not_found(self):
        """Test retrieval of non-existent string."""
        url = reverse('string-detail', kwargs={'string_value': 'nonexistent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_string_success(self):
        """Test successful string deletion."""
        # First create a string
        url = reverse('string-list-create')
        data = {'value': 'hello world'}
        self.client.post(url, data, format='json')

        # Then delete it
        url = reverse('string-detail', kwargs={'string_value': 'hello world'})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify it's gone
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_string_not_found(self):
        """Test deletion of non-existent string."""
        url = reverse('string-detail', kwargs={'string_value': 'nonexistent'})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_strings_list_empty(self):
        """Test getting list of strings when empty."""
        url = reverse('string-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['data']), 0)

    def test_get_strings_list_with_data(self):
        """Test getting list of strings with data."""
        url = reverse('string-list-create')
        data1 = {'value': 'hello world'}
        data2 = {'value': 'radar'}
        self.client.post(url, data1, format='json')
        self.client.post(url, data2, format='json')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['data']), 2)

    def test_get_strings_filter_is_palindrome(self):
        """Test filtering by is_palindrome."""
        url = reverse('string-list-create')
        self.client.post(url, {'value': 'hello world'}, format='json')  # Not palindrome
        self.client.post(url, {'value': 'radar'}, format='json')  # Palindrome

        # Filter for palindromes
        response = self.client.get(url, {'is_palindrome': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['value'], 'radar')

        # Filter for non-palindromes
        response = self.client.get(url, {'is_palindrome': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['value'], 'hello world')

    def test_get_strings_filter_min_length(self):
        """Test filtering by min_length."""
        url = reverse('string-list-create')
        self.client.post(url, {'value': 'hi'}, format='json')  # Length 2
        self.client.post(url, {'value': 'hello world'}, format='json')  # Length 11

        response = self.client.get(url, {'min_length': '5'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['value'], 'hello world')

    def test_get_strings_filter_max_length(self):
        """Test filtering by max_length."""
        url = reverse('string-list-create')
        self.client.post(url, {'value': 'hi'}, format='json')  # Length 2
        self.client.post(url, {'value': 'hello world'}, format='json')  # Length 11

        response = self.client.get(url, {'max_length': '5'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['value'], 'hi')

    def test_get_strings_filter_word_count(self):
        """Test filtering by word_count."""
        url = reverse('string-list-create')
        self.client.post(url, {'value': 'hello'}, format='json')  # 1 word
        self.client.post(url, {'value': 'hello world'}, format='json')  # 2 words

        response = self.client.get(url, {'word_count': '1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['value'], 'hello')

    def test_get_strings_filter_contains_character(self):
        """Test filtering by contains_character."""
        url = reverse('string-list-create')
        self.client.post(url, {'value': 'hello'}, format='json')  # Contains 'h'
        self.client.post(url, {'value': 'world'}, format='json')  # Does not contain 'h'

        response = self.client.get(url, {'contains_character': 'h'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['value'], 'hello')

    def test_get_strings_filter_invalid_min_length(self):
        """Test invalid min_length parameter."""
        url = reverse('string-list-create')
        response = self.client.get(url, {'min_length': 'invalid'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_get_strings_filter_invalid_contains_character(self):
        """Test invalid contains_character parameter (not single character)."""
        url = reverse('string-list-create')
        response = self.client.get(url, {'contains_character': 'ab'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_natural_language_filter_single_word_palindromic(self):
        """Test natural language filter for single word palindromic strings."""
        url = reverse('string-natural-language-filter')
        self.client.post(reverse('string-list-create'), {'value': 'radar'}, format='json')  # Palindrome, 1 word
        self.client.post(reverse('string-list-create'), {'value': 'hello world'}, format='json')  # Not palindrome, 2 words

        response = self.client.get(url, {'query': 'all single word palindromic strings'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['value'], 'radar')
        self.assertIn('word_count', response.data['interpreted_query']['parsed_filters'])
        self.assertIn('is_palindrome', response.data['interpreted_query']['parsed_filters'])

    def test_natural_language_filter_longer_than(self):
        """Test natural language filter for strings longer than X characters."""
        url = reverse('string-natural-language-filter')
        self.client.post(reverse('string-list-create'), {'value': 'hi'}, format='json')  # Length 2
        self.client.post(reverse('string-list-create'), {'value': 'hello world'}, format='json')  # Length 11

        response = self.client.get(url, {'query': 'strings longer than 5 characters'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['value'], 'hello world')

    def test_natural_language_filter_containing_letter(self):
        """Test natural language filter for strings containing a specific letter."""
        url = reverse('string-natural-language-filter')
        self.client.post(reverse('string-list-create'), {'value': 'hello'}, format='json')  # Contains 'h'
        self.client.post(reverse('string-list-create'), {'value': 'world'}, format='json')  # Does not contain 'h'

        response = self.client.get(url, {'query': 'strings containing the letter h'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['value'], 'hello')

    def test_natural_language_filter_missing_query(self):
        """Test natural language filter with missing query parameter."""
        url = reverse('string-natural-language-filter')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_natural_language_filter_empty_results(self):
        """Test natural language filter with no matching results."""
        url = reverse('string-natural-language-filter')
        response = self.client.get(url, {'query': 'all single word palindromic strings'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['data']), 0)
