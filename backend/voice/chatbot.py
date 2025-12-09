import os
import requests
from typing import Optional, Dict
import random

class QuoteChatbot:
    
    def __init__(self, quotes_api_url: str = "http://localhost:8000/api/v1/quotes/search/", use_rag: bool = True):
        self.use_rag = use_rag and os.getenv('ENABLE_RAG', 'false').lower() == 'true'
        self.quotes_api_url = quotes_api_url
        
        if self.use_rag:
            from rag.rag_chatbot import RAGChatbot
            
            llm_provider = os.getenv('LLM_PROVIDER', 'ollama')
            
            llm_config = {}
            if llm_provider == 'ollama':
                llm_config = {
                    'model': os.getenv('OLLAMA_MODEL', 'llama3.2:3b'),
                    'base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
                }
            elif llm_provider == 'openai':
                llm_config = {'api_key': os.getenv('OPENAI_API_KEY')}
            elif llm_provider == 'anthropic':
                llm_config = {'api_key': os.getenv('ANTHROPIC_API_KEY')}
            
            self.rag_bot = RAGChatbot(
                neo4j_uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
                neo4j_user=os.getenv('NEO4J_USER', 'neo4j'),
                neo4j_password=os.getenv('NEO4J_PASSWORD'),
                llm_provider=llm_provider,
                llm_config=llm_config
            )
            print(f"✓ RAG Chatbot initialized with {llm_provider}")

    def get_personalized_greeting(self, username: str, accent: str = 'american') -> str:
        """Generate personalized greeting based on accent"""
        greetings = {
            'american': [
                f"Hey {username}! How can I help you today?",
                f"Hi {username}! What quote are you looking for?",
                f"Hello {username}! Ready to discover some wisdom?"
            ],
            'uk': [
                f"Good day, {username}! How may I assist you?",
                f"Hello {username}! What wisdom shall we seek today?",
                f"Greetings {username}! Ready for some brilliant quotes?"
            ],
            'irish': [
                f"Top of the morning, {username}! What can I do for you?",
                f"Hello there, {username}! Looking for some wise words?",
                f"Good day to you, {username}! What quote shall we find?"
            ],
            'indian': [
                f"Namaste {username}! How can I help you today?",
                f"Hello {username}! What wisdom are you seeking?",
                f"Greetings {username}! Ready to explore quotes?"
            ],
            'african': [
                f"Hello {username}! What can I do for you today?",
                f"Greetings {username}! Looking for some wisdom?",
                f"Welcome {username}! What quote interests you?"
            ],
            'mexican': [
                f"¡Hola {username}! ¿Cómo puedo ayudarte?",
                f"¡Buenos días {username}! ¿Qué cita buscas?",
                f"¡Saludos {username}! ¿Listo para descubrir sabiduría?"
            ],
            'french': [
                f"Bonjour {username}! Comment puis-je vous aider?",
                f"Salut {username}! Quelle citation cherchez-vous?",
                f"Bienvenue {username}! Prêt pour des citations?"
            ],
            'italian': [
                f"Ciao {username}! Come posso aiutarti?",
                f"Salve {username}! Quale citazione cerchi?",
                f"Benvenuto {username}! Pronto per le citazioni?"
            ],
            'german': [
                f"Guten Tag {username}! Wie kann ich helfen?",
                f"Hallo {username}! Welches Zitat suchen Sie?",
                f"Willkommen {username}! Bereit für Zitate?"
            ]
        }
        
        accent_greetings = greetings.get(accent, greetings['american'])
        return random.choice(accent_greetings)
    
    def craft_response(self, user_query: str, quote_data: Optional[Dict] = None, 
                      username: str = None, accent: str = 'american') -> str:
        """Craft response with personalization"""
        
        if not quote_data:
            return self._no_quote_response(user_query, username, accent)
        
        quote_text = quote_data.get('text', '')
        author = quote_data.get('author', 'Unknown')
        work = quote_data.get('work', '')
        
        # Personalized intros based on accent
        intros = {
            'american': [
                f"Great question{', ' + username if username else ''}!",
                f"I found something perfect{' for you, ' + username if username else ''}!",
                f"Check this out{', ' + username if username else ''}!"
            ],
            'uk': [
                f"Splendid question{', ' + username if username else ''}!",
                f"I've found something rather fitting{' for you, ' + username if username else ''}!",
                f"Do have a look at this{', ' + username if username else ''}!"
            ],
            'irish': [
                f"Grand question{', ' + username if username else ''}!",
                f"I've got just the thing{' for you, ' + username if username else ''}!",
                f"Take a gander at this{', ' + username if username else ''}!"
            ],
            'mexican': [
                f"¡Excelente pregunta{', ' + username if username else ''}!",
                f"¡Encontré algo perfecto{' para ti, ' + username if username else ''}!",
                f"¡Mira esto{', ' + username if username else ''}!"
            ],
            'french': [
                f"Excellente question{', ' + username if username else ''}!",
                f"J'ai trouvé quelque chose de parfait{' pour vous, ' + username if username else ''}!",
                f"Regardez ceci{', ' + username if username else ''}!"
            ],
            'italian': [
                f"Ottima domanda{', ' + username if username else ''}!",
                f"Ho trovato qualcosa di perfetto{' per te, ' + username if username else ''}!",
                f"Guarda questo{', ' + username if username else ''}!"
            ],
            'german': [
                f"Gute Frage{', ' + username if username else ''}!",
                f"Ich habe etwas Perfektes gefunden{' für Sie, ' + username if username else ''}!",
                f"Sehen Sie sich das an{', ' + username if username else ''}!"
            ]
        }
        
        intro = random.choice(intros.get(accent, intros['american']))
        
        # Build response
        if work:
            response = f"{intro} {author} said in {work}: {quote_text}"
        else:
            response = f"{intro} {author} once said: {quote_text}"
        
        return response
    
    def _no_quote_response(self, query: str, username: str = None, accent: str = 'american') -> str:
        """Response when no quote found"""
        responses = {
            'american': [
                f"Sorry{', ' + username if username else ''}, I couldn't find a quote for that. Try rephrasing?",
                f"Hmm{', ' + username if username else ''}, no matches. Want to try different keywords?",
            ],
            'uk': [
                f"Apologies{', ' + username if username else ''}, I couldn't locate a suitable quote. Perhaps rephrase?",
                f"I'm afraid{', ' + username if username else ''} I found nothing. Try different terms?",
            ],
            'mexican': [
                f"Lo siento{', ' + username if username else ''}, no encontré una cita. ¿Intentar de nuevo?",
                f"Disculpa{', ' + username if username else ''}, sin resultados. ¿Otra búsqueda?",
            ],
            'french': [
                f"Désolé{', ' + username if username else ''}, aucune citation trouvée. Reformuler?",
                f"Pardon{', ' + username if username else ''}, pas de résultats. Essayer autrement?",
            ],
            'italian': [
                f"Scusa{', ' + username if username else ''}, nessuna citazione trovata. Riformulare?",
                f"Mi dispiace{', ' + username if username else ''}, nessun risultato. Provare diversamente?",
            ],
            'german': [
                f"Entschuldigung{', ' + username if username else ''}, kein Zitat gefunden. Umformulieren?",
                f"Tut mir leid{', ' + username if username else ''}, keine Ergebnisse. Anders versuchen?",
            ]
        }
        
        accent_responses = responses.get(accent, responses['american'])
        return random.choice(accent_responses)
    
    def process_query(self, user_query: str, username: str = None, accent: str = 'american') -> Dict:
        """Full pipeline with personalization"""
        quote_data = self.search_quote(user_query)
        response_text = self.craft_response(user_query, quote_data, username, accent)
        
        return {
            'query': user_query,
            'response': response_text,
            'quote_found': quote_data is not None,
            'quote_data': quote_data
        }
