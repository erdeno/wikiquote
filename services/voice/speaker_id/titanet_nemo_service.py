import nemo.collections.asr as nemo_asr
import torch
import numpy as np
from typing import Dict, Optional, List
import tempfile
import os
import json
import soundfile as sf

class NeMoSpeakerRecognition:
    """
    Speaker Recognition using NeMo TitaNet
    """
    
    def __init__(self, model_name: str = "titanet_large"):
        """
        Initialize NeMo TitaNet model
        
        Args:
            model_name: Model variant (titanet_large, titanet_small)
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading NeMo TitaNet model '{model_name}' on {self.device}...")
        
        # Load pre-trained TitaNet model
        if model_name == "titanet_large":
            self.model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained(
                "nvidia/speakerverification_en_titanet_large"
            )
        else:
            self.model = nemo_asr.models.EncDecSpeakerLabelModel.from_pretrained(
                "nvidia/speakerverification_en_titanet_small"
            )
        
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Speaker embeddings database (in production, use real DB)
        self.speaker_embeddings: Dict[str, np.ndarray] = {}
        self.embedding_file = "speaker_embeddings.json"
        
        # Load existing embeddings if available
        self._load_embeddings()
        
        print("NeMo TitaNet model loaded successfully.")
    
    def _load_embeddings(self):
        """Load speaker embeddings from file"""
        if os.path.exists(self.embedding_file):
            try:
                with open(self.embedding_file, 'r') as f:
                    data = json.load(f)
                    # Convert lists back to numpy arrays
                    self.speaker_embeddings = {
                        k: np.array(v) for k, v in data.items()
                    }
                print(f"Loaded {len(self.speaker_embeddings)} speaker profiles")
            except Exception as e:
                print(f"Error loading embeddings: {e}")
    
    def _save_embeddings(self):
        """Save speaker embeddings to file"""
        try:
            # Convert numpy arrays to lists for JSON serialization
            data = {
                k: v.tolist() for k, v in self.speaker_embeddings.items()
            }
            with open(self.embedding_file, 'w') as f:
                json.dump(data, f)
            print(f"Saved {len(self.speaker_embeddings)} speaker profiles")
        except Exception as e:
            print(f"Error saving embeddings: {e}")
    
    def extract_embedding(self, audio_path: str) -> np.ndarray:
        """
        Extract speaker embedding from audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Speaker embedding as numpy array
        """
        # Verify audio meets minimum requirements
        audio_data, sample_rate = sf.read(audio_path)
        
        # TitaNet expects at least 0.5 seconds of audio
        min_samples = int(0.5 * sample_rate)
        if len(audio_data) < min_samples:
            raise ValueError(f"Audio too short. Need at least 0.5 seconds, got {len(audio_data)/sample_rate:.2f}s")
        
        # Get embedding
        with torch.no_grad():
            # NeMo models expect list of file paths
            emb = self.model.get_embedding(audio_path)
            
            # Convert to numpy
            if isinstance(emb, torch.Tensor):
                emb = emb.cpu().numpy()
            
            # Flatten if needed
            if len(emb.shape) > 1:
                emb = emb.flatten()
        
        return emb
    
    def extract_embedding_bytes(self, audio_bytes: bytes) -> np.ndarray:
        """
        Extract embedding from audio bytes
        
        Args:
            audio_bytes: Audio data as bytes
            
        Returns:
            Speaker embedding
        """
        # Write to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            embedding = self.extract_embedding(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
        return embedding
    
    def register_speaker(self, speaker_id: str, audio_bytes: bytes) -> Dict:
        """
        Register a new speaker with their voice sample
        
        Args:
            speaker_id: Unique identifier for the speaker
            audio_bytes: Audio sample for registration
            
        Returns:
            Dict with success status and message
        """
        try:
            # Extract embedding
            embedding = self.extract_embedding_bytes(audio_bytes)
            
            # Store embedding
            self.speaker_embeddings[speaker_id] = embedding
            
            # Save to file
            self._save_embeddings()
            
            print(f"✓ Registered speaker: {speaker_id}")
            
            return {
                'success': True,
                'speaker_id': speaker_id,
                'embedding_dim': len(embedding),
                'message': f'Speaker {speaker_id} registered successfully'
            }
            
        except Exception as e:
            print(f"✗ Failed to register speaker {speaker_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def identify_speaker(
        self, 
        audio_bytes: bytes, 
        threshold: float = 0.7
    ) -> Optional[Dict]:
        """
        Identify speaker from audio
        
        Args:
            audio_bytes: Audio data
            threshold: Cosine similarity threshold (0-1, higher = more strict)
            
        Returns:
            Dict with speaker_id, confidence, or None if no match
        """
        if not self.speaker_embeddings:
            return None
        
        try:
            # Extract query embedding
            query_embedding = self.extract_embedding_bytes(audio_bytes)
            
            # Compute cosine similarity with all registered speakers
            best_match = None
            best_score = -1.0
            
            for speaker_id, stored_embedding in self.speaker_embeddings.items():
                # Cosine similarity
                similarity = self._cosine_similarity(query_embedding, stored_embedding)
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = speaker_id
            
            # Check threshold
            if best_score >= threshold:
                print(f"✓ Identified speaker: {best_match} (confidence: {best_score:.3f})")
                return {
                    'speaker_id': best_match,
                    'confidence': float(best_score),
                    'threshold': threshold
                }
            else:
                print(f"✗ No confident match (best score: {best_score:.3f}, threshold: {threshold})")
                return None
                
        except Exception as e:
            print(f"Error during speaker identification: {e}")
            return None
    
    def verify_speaker(
        self,
        speaker_id: str,
        audio_bytes: bytes,
        threshold: float = 0.7
    ) -> Dict:
        """
        Verify if audio matches a specific speaker
        
        Args:
            speaker_id: Speaker to verify against
            audio_bytes: Audio data
            threshold: Similarity threshold
            
        Returns:
            Dict with verification result
        """
        if speaker_id not in self.speaker_embeddings:
            return {
                'verified': False,
                'error': f'Speaker {speaker_id} not registered'
            }
        
        try:
            query_embedding = self.extract_embedding_bytes(audio_bytes)
            stored_embedding = self.speaker_embeddings[speaker_id]
            
            similarity = self._cosine_similarity(query_embedding, stored_embedding)
            verified = similarity >= threshold
            
            return {
                'verified': verified,
                'speaker_id': speaker_id,
                'confidence': float(similarity),
                'threshold': threshold
            }
            
        except Exception as e:
            return {
                'verified': False,
                'error': str(e)
            }
    
    def _cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            emb1: First embedding
            emb2: Second embedding
            
        Returns:
            Cosine similarity score (0-1)
        """
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Normalize to 0-1 range (cosine similarity is -1 to 1)
        return float((similarity + 1) / 2)
    
    def get_registered_speakers(self) -> List[Dict]:
        """
        Get list of all registered speakers
        
        Returns:
            List of dicts with speaker info
        """
        return [
            {
                'speaker_id': speaker_id,
                'embedding_dim': len(embedding),
                'registered': True
            }
            for speaker_id, embedding in self.speaker_embeddings.items()
        ]
    
    def delete_speaker(self, speaker_id: str) -> bool:
        """
        Delete a registered speaker
        
        Args:
            speaker_id: Speaker to delete
            
        Returns:
            True if deleted, False if not found
        """
        if speaker_id in self.speaker_embeddings:
            del self.speaker_embeddings[speaker_id]
            self._save_embeddings()
            print(f"✓ Deleted speaker: {speaker_id}")
            return True
        return False
    
    def get_embedding_stats(self) -> Dict:
        """
        Get statistics about registered embeddings
        
        Returns:
            Dict with statistics
        """
        if not self.speaker_embeddings:
            return {
                'num_speakers': 0,
                'embedding_dim': None
            }
        
        first_emb = next(iter(self.speaker_embeddings.values()))
        
        return {
            'num_speakers': len(self.speaker_embeddings),
            'embedding_dim': len(first_emb),
            'speakers': list(self.speaker_embeddings.keys())
        }
