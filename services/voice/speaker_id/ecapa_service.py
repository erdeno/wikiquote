import torch
import torchaudio
from speechbrain.pretrained import EncoderClassifier
import numpy as np
from typing import Dict, Optional, List
import os
import tempfile
import json

class SpeakerIdentifier:
    """
    Speaker Recognition using SpeechBrain ECAPA-TDNN
    """
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading ECAPA-TDNN model on {self.device}...")
        
        self.classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/spkrec-ecapa-voxceleb",
            run_opts={"device": self.device}
        )
        
        # In-memory speaker embeddings database
        self.speaker_embeddings: Dict[str, np.ndarray] = {}
        self.embedding_file = "speaker_embeddings.json"
        
        self._load_embeddings()
        print("Speaker identification model loaded.")
    
    def _load_embeddings(self):
        """Load speaker embeddings from file"""
        if os.path.exists(self.embedding_file):
            try:
                with open(self.embedding_file, 'r') as f:
                    data = json.load(f)
                    self.speaker_embeddings = {
                        k: np.array(v) for k, v in data.items()
                    }
                print(f"Loaded {len(self.speaker_embeddings)} speaker profiles")
            except Exception as e:
                print(f"Error loading embeddings: {e}")
    
    def _save_embeddings(self):
        """Save speaker embeddings to file"""
        try:
            data = {k: v.tolist() for k, v in self.speaker_embeddings.items()}
            with open(self.embedding_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving embeddings: {e}")
    
    def extract_embedding(self, audio_path: str) -> np.ndarray:
        """Extract speaker embedding from audio file"""
        signal, fs = torchaudio.load(audio_path)
        
        if fs != 16000:
            resampler = torchaudio.transforms.Resample(fs, 16000)
            signal = resampler(signal)
        
        with torch.no_grad():
            embedding = self.classifier.encode_batch(signal)
        
        return embedding.squeeze().cpu().numpy()
    
    def extract_embedding_bytes(self, audio_bytes: bytes) -> np.ndarray:
        """Extract embedding from audio bytes"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            embedding = self.extract_embedding(tmp_path)
        finally:
            os.unlink(tmp_path)
        
        return embedding
    
    def register_speaker(self, speaker_id: str, audio_bytes: bytes) -> bool:
        """Register a new speaker"""
        try:
            embedding = self.extract_embedding_bytes(audio_bytes)
            self.speaker_embeddings[speaker_id] = embedding
            self._save_embeddings()
            print(f"Registered speaker: {speaker_id}")
            return True
        except Exception as e:
            print(f"Failed to register speaker {speaker_id}: {e}")
            return False
    
    def identify_speaker(self, audio_bytes: bytes, threshold: float = 0.25) -> Optional[str]:
        """
        Identify speaker from audio
        Returns speaker_id or None
        """
        if not self.speaker_embeddings:
            return None
        
        query_embedding = self.extract_embedding_bytes(audio_bytes)
        
        best_match = None
        best_score = float('inf')
        
        for speaker_id, stored_embedding in self.speaker_embeddings.items():
            distance = np.linalg.norm(query_embedding - stored_embedding)
            
            if distance < best_score:
                best_score = distance
                best_match = speaker_id
        
        if best_score < threshold:
            return best_match
        
        return None
    
    def get_registered_speakers(self) -> list:
        """Get list of registered speaker IDs"""
        return list(self.speaker_embeddings.keys())