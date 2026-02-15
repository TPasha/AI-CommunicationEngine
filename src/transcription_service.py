"""
Speech-to-Text (STT) Transcription Service
Handles real-time audio transcription with speaker identification
"""

import asyncio
import io
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

logger = logging.getLogger(__name__)


class TranscriptionProvider(str, Enum):
    """Available transcription providers"""
    OPENAI_WHISPER = "openai_whisper"
    HUGGINGFACE_WHISPER = "huggingface_whisper"
    GOOGLE_CLOUD = "google_cloud"
    AZURE = "azure"
    AWS = "aws"
    LOCAL = "local"


class TranscriptionResult:
    """Container for transcription output"""
    
    def __init__(
        self,
        text: str,
        confidence: float,
        duration: float,
        speaker_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        self.text = text
        self.confidence = confidence
        self.duration = duration
        self.speaker_id = speaker_id
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "duration": self.duration,
            "speaker_id": self.speaker_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    def __repr__(self):
        return f"<TranscriptionResult(text_len={len(self.text)}, confidence={self.confidence:.2f})>"


class TranscriptionService:
    """Main transcription service"""
    
    def __init__(
        self,
        provider: str = "openai_whisper",
        api_key: Optional[str] = None,
        model: str = "whisper-1",
        language: str = "en",
        timeout_ms: int = 2000
    ):
        self.provider = TranscriptionProvider(provider)
        self.api_key = api_key
        self.model = model
        self.language = language
        self.timeout_seconds = timeout_ms / 1000
        
        self._initialize_provider()
        self.speaker_profiles = {}
    
    def _initialize_provider(self):
        """Initialize the transcription provider"""
        if self.provider == TranscriptionProvider.OPENAI_WHISPER:
            if not HAS_OPENAI:
                raise ImportError("openai package required for Whisper support")
            if self.api_key:
                openai.api_key = self.api_key
        
        elif self.provider == TranscriptionProvider.HUGGINGFACE_WHISPER:
            if not HAS_TRANSFORMERS:
                raise ImportError("transformers package required for Hugging Face Whisper support")
            # Initialize the Hugging Face pipeline
            self.hf_pipeline = pipeline(
                "automatic-speech-recognition",
                model=self.model
            )
        
        logger.info(f"Initialized transcription service: {self.provider}")
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        speaker_id: Optional[str] = None,
        sample_rate: int = 16000
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe audio bytes to text
        
        Args:
            audio_data: Raw audio bytes
            speaker_id: Optional speaker identifier
            sample_rate: Audio sample rate in Hz
            
        Returns:
            TranscriptionResult or None
        """
        try:
            if self.provider == TranscriptionProvider.OPENAI_WHISPER:
                return await self._transcribe_whisper(audio_data, speaker_id)
            elif self.provider == TranscriptionProvider.HUGGINGFACE_WHISPER:
                return await self._transcribe_huggingface(audio_data, speaker_id)
            else:
                logger.warning(f"Provider {self.provider} not implemented")
                return None
        
        except asyncio.TimeoutError:
            logger.error(f"Transcription timeout for speaker {speaker_id}")
            return None
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return None
    
    async def _transcribe_whisper(
        self,
        audio_data: bytes,
        speaker_id: Optional[str] = None
    ) -> Optional[TranscriptionResult]:
        """Transcribe using OpenAI Whisper API"""
        try:
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    openai.Audio.transcribe,
                    model=self.model,
                    file=audio_file,
                    language=self.language
                ),
                timeout=self.timeout_seconds
            )
            
            confidence = response.get("confidence", 0.85)
            text = response.get("text", "").strip()
            
            if not text:
                logger.warning("Empty transcription result")
                return None
            
            result = TranscriptionResult(
                text=text,
                confidence=confidence,
                duration=len(audio_data) / (16000 * 2),
                speaker_id=speaker_id,
                metadata={"provider": "whisper"}
            )
            
            logger.info(f"Transcribed {len(text)} chars from speaker {speaker_id}")
            return result
        
        except asyncio.TimeoutError:
            raise
        except Exception as e:
            logger.error(f"Whisper API error: {str(e)}")
            return None
    
    async def _transcribe_huggingface(
        self,
        audio_data: bytes,
        speaker_id: Optional[str] = None
    ) -> Optional[TranscriptionResult]:
        """Transcribe using Hugging Face Whisper model"""
        try:
            # Try to load audio using librosa (handles WebM, MP3, etc.)
            try:
                import librosa
                import numpy as np
                
                # Load audio from bytes
                y, sr = librosa.load(io.BytesIO(audio_data), sr=16000, mono=True)
                logger.info(f"Loaded audio using librosa: {len(y)} samples at {sr}Hz")
                
                # Convert to the format Whisper expects
                # The pipeline can accept numpy arrays
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.hf_pipeline,
                        y,
                        sampling_rate=sr,
                        language=self.language if self.language != "en" else None
                    ),
                    timeout=self.timeout_seconds
                )
            except ImportError:
                # Fallback: try using io.BytesIO directly
                logger.warning("librosa not available, trying direct BytesIO")
                audio_file = io.BytesIO(audio_data)
                
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.hf_pipeline,
                        audio_file,
                        language=self.language if self.language != "en" else None
                    ),
                    timeout=self.timeout_seconds
                )
            
            text = response.get("text", "").strip()
            
            if not text:
                logger.warning("Empty transcription result from Hugging Face")
                return None
            
            # Hugging Face doesn't provide confidence scores, use default
            result = TranscriptionResult(
                text=text,
                confidence=0.85,
                duration=len(audio_data) / (16000 * 2),
                speaker_id=speaker_id,
                metadata={"provider": "huggingface_whisper", "model": self.model}
            )
            
            logger.info(f"Transcribed {len(text)} chars from speaker {speaker_id} using Hugging Face")
            return result
        
        except asyncio.TimeoutError:
            raise
        except Exception as e:
            logger.error(f"Hugging Face Whisper error: {str(e)}")
            return None
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return [
            "en", "es", "fr", "de", "it", "ja", "ko", "zh", "ru", "ar", "pt"
        ]


class BatchTranscriptionService:
    """Service for transcribing multiple audio streams concurrently"""
    
    def __init__(self, max_concurrent: int = 10):
        self.transcription_service = TranscriptionService()
        self.max_concurrent = max_concurrent
        self.active_transcriptions = {}
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def transcribe_batch(
        self,
        audio_stream_map: Dict[str, bytes],
        sources: Optional[Dict[str, str]] = None
    ) -> Dict[str, Optional[TranscriptionResult]]:
        """
        Transcribe multiple audio streams concurrently
        
        Args:
            audio_stream_map: {stream_id: audio_bytes}
            sources: Optional source mapping
            
        Returns:
            {stream_id: TranscriptionResult or None}
        """
        tasks = []
        for stream_id, audio_data in audio_stream_map.items():
            task = self._transcribe_with_semaphore(stream_id, audio_data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return dict(zip(audio_stream_map.keys(), results))
    
    async def _transcribe_with_semaphore(
        self,
        stream_id: str,
        audio_data: bytes
    ) -> Optional[TranscriptionResult]:
        """Transcribe with concurrency limit"""
        async with self.semaphore:
            self.active_transcriptions[stream_id] = True
            try:
                return await self.transcription_service.transcribe_audio(
                    audio_data, stream_id
                )
            finally:
                if stream_id in self.active_transcriptions:
                    del self.active_transcriptions[stream_id]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    svc = TranscriptionService(provider="openai_whisper")
    print("Transcription Service initialized successfully")
    print(f"Supported languages: {svc.get_supported_languages()}")
