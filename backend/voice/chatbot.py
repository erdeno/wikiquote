import requests
from typing import Optional, Dict
import random

class QuoteChatbot:
    """
    Chatbot that finds relevant quotes and crafts conversational responses
    """
    
    def __init__(self, quotes_api_url: str = "http://localhost:8000/api/v1/quotes/search/"):
        self.quotes_api_url = quotes_api_url
        
    def search_quote(self, query: str) -> Optional[Dict]:
        """
        Search for a quote using the Django quotes API
        """
        try:
            response = requests.get(self.quotes_api_url, params={'q': query})
            if response.status_code == 200:
                data = response.json()
                if data.get('results') and len(data['results']) > 0:
                    return data['results'][0]  # Return best match
            return None
        except Exception as e:
            print(f"Error searching quotes: {e}")
            return None
    
    def craft_response(self, user_query: str, quote_data: Optional[Dict] = None) -> str:
        """
        Craft a natural conversational response
        """
        if not quote_data:
            return self._no_quote_response(user_query)
        
        quote_text = quote_data.get('text', '')
        author = quote_data.get('author', 'Unknown')
        work = quote_data.get('work', '')
        
        # Choose a response template
        templates = [
            f"{author} once said: {quote_text}",
            f"Here's a quote from {author}: {quote_text}",
            f"I found this from {author}: {quote_text}",
            f"{author} had something relevant: {quote_text}",
        ]
        
        if work:
            templates.extend([
                f"From {author}'s {work}: {quote_text}",
                f"In {work}, {author} wrote: {quote_text}",
            ])
        
        return random.choice(templates)
    
    def _no_quote_response(self, query: str) -> str:
        """
        Response when no quote is found
        """
        responses = [
            "I couldn't find a relevant quote for that. Could you try rephrasing?",
            "Hmm, I don't have a quote that matches. Try asking differently.",
            "No matching quote found. What else can I help you with?",
        ]
        return random.choice(responses)
    
    def process_query(self, user_query: str) -> Dict:
        """
        Full pipeline: search + craft response
        """
        quote_data = self.search_quote(user_query)
        response_text = self.craft_response(user_query, quote_data)
        
        return {
            'query': user_query,
            'response': response_text,
            'quote_found': quote_data is not None,
            'quote_data': quote_data
        }