import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
class TestQuoteChatbot:
    """Test chatbot functionality"""
    
    def test_chatbot_initialization(self):
        """Test chatbot initializes"""
        from backend.voice.chatbot import QuoteChatbot
        
        chatbot = QuoteChatbot()
        assert chatbot is not None
    
    @patch('backend.voice.chatbot.requests.get')
    def test_search_quote_success(self, mock_get):
        """Test successful quote search"""
        from backend.voice.chatbot import QuoteChatbot
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{
                'text': 'Test quote',
                'author': 'Test Author',
                'work': 'Test Work'
            }]
        }
        mock_get.return_value = mock_response
        
        chatbot = QuoteChatbot()
        result = chatbot.search_quote('test query')
        
        assert result is not None
        assert result['text'] == 'Test quote'
    
    @patch('backend.voice.chatbot.requests.get')
    def test_search_quote_no_results(self, mock_get):
        """Test quote search with no results"""
        from backend.voice.chatbot import QuoteChatbot
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': []}
        mock_get.return_value = mock_response
        
        chatbot = QuoteChatbot()
        result = chatbot.search_quote('nonexistent')
        
        assert result is None
    
    def test_craft_response_with_quote(self):
        """Test crafting response with quote"""
        from backend.voice.chatbot import QuoteChatbot
        
        chatbot = QuoteChatbot()
        quote_data = {
            'text': 'Test quote',
            'author': 'Test Author',
            'work': 'Test Work'
        }
        
        response = chatbot.craft_response('test query', quote_data)
        
        assert 'Test Author' in response
        assert 'Test quote' in response
    
    def test_craft_response_no_quote(self):
        """Test crafting response without quote"""
        from backend.voice.chatbot import QuoteChatbot
        
        chatbot = QuoteChatbot()
        response = chatbot.craft_response('test query', None)
        
        assert "couldn't find" in response.lower() or "no" in response.lower()
    
    @patch('backend.voice.chatbot.requests.get')
    def test_process_query(self, mock_get):
        """Test full query processing"""
        from backend.voice.chatbot import QuoteChatbot
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{
                'text': 'Test quote',
                'author': 'Test Author'
            }]
        }
        mock_get.return_value = mock_response
        
        chatbot = QuoteChatbot()
        result = chatbot.process_query('test query')
        
        assert 'query' in result
        assert 'response' in result
        assert 'quote_found' in result
        assert result['quote_found'] is True