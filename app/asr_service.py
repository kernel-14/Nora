"""ASR (Automatic Speech Recognition) service for Voice Text Processor.

This module implements the ASRService class for transcribing audio files
to text using the Zhipu AI GLM-ASR-2512 API.

Requirements: 2.1, 2.2, 2.3, 2.4, 9.2, 9.5
"""

import logging
from typing import Optional
import httpx


logger = logging.getLogger(__name__)


class ASRServiceError(Exception):
    """Exception raised when ASR service operations fail.
    
    This exception is raised when the Zhipu ASR API call fails,
    such as due to network issues, API errors, or invalid responses.
    
    Requirements: 2.3
    """
    
    def __init__(self, message: str = "语音识别服务不可用"):
        """Initialize ASRServiceError.
        
        Args:
            message: Error message describing the failure
        """
        super().__init__(message)
        self.message = message


class ASRService:
    """Service for transcribing audio files using Zhipu AI ASR API.
    
    This service handles audio file transcription by calling the Zhipu AI
    GLM-ASR-2512 API. It manages API authentication, request formatting,
    response parsing, and error handling.
    
    Attributes:
        api_key: Zhipu AI API key for authentication
        client: Async HTTP client for making API requests
        api_url: Zhipu AI ASR API endpoint URL
        model: ASR model identifier
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 9.2, 9.5
    """
    
    def __init__(self, api_key: str):
        """Initialize the ASR service.
        
        Args:
            api_key: Zhipu AI API key for authentication
        """
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self.api_url = "https://api.z.ai/api/paas/v4/audio/transcriptions"
        self.model = "glm-asr-2512"
    
    async def close(self):
        """Close the HTTP client.
        
        This should be called when the service is no longer needed
        to properly clean up resources.
        """
        await self.client.aclose()
    
    async def transcribe(self, audio_file: bytes, filename: str = "audio.mp3") -> str:
        """Transcribe audio file to text using Zhipu ASR API.
        
        This method sends the audio file to the Zhipu AI ASR API and returns
        the transcribed text. It handles API errors, empty recognition results,
        and logs all errors with timestamps and stack traces.
        
        Args:
            audio_file: Audio file content as bytes
            filename: Name of the audio file (for API request)
        
        Returns:
            Transcribed text content. Returns empty string if audio cannot
            be recognized (empty recognition result).
        
        Raises:
            ASRServiceError: If API call fails or returns invalid response
        
        Requirements: 2.1, 2.2, 2.3, 2.4, 9.2, 9.5
        """
        try:
            # Prepare request headers
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Prepare multipart form data
            files = {
                "file": (filename, audio_file, "audio/mpeg")
            }
            
            data = {
                "model": self.model,
                "stream": "false"
            }
            
            logger.info(f"Calling Zhipu ASR API for file: {filename}")
            
            # Make API request
            response = await self.client.post(
                self.api_url,
                headers=headers,
                files=files,
                data=data
            )
            
            # Check response status
            if response.status_code != 200:
                error_msg = f"ASR API returned status {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f": {error_detail}"
                except Exception:
                    error_msg += f": {response.text}"
                
                logger.error(
                    f"ASR API call failed: {error_msg}",
                    exc_info=True,
                    extra={"timestamp": logger.makeRecord(
                        logger.name, logging.ERROR, "", 0, error_msg, (), None
                    ).created}
                )
                raise ASRServiceError(f"语音识别服务不可用: {error_msg}")
            
            # Parse response
            try:
                result = response.json()
            except Exception as e:
                error_msg = f"Failed to parse ASR API response: {str(e)}"
                logger.error(
                    error_msg,
                    exc_info=True,
                    extra={"timestamp": logger.makeRecord(
                        logger.name, logging.ERROR, "", 0, error_msg, (), None
                    ).created}
                )
                raise ASRServiceError(f"语音识别服务不可用: 响应格式无效")
            
            # Extract transcribed text
            text = result.get("text", "")
            
            # Handle empty recognition result
            if not text or text.strip() == "":
                logger.warning(
                    f"ASR returned empty text for file: {filename}. "
                    "Audio content may be unrecognizable."
                )
                return ""
            
            logger.info(
                f"ASR transcription successful for {filename}. "
                f"Text length: {len(text)} characters"
            )
            
            return text
            
        except ASRServiceError:
            # Re-raise ASRServiceError as-is
            raise
            
        except httpx.TimeoutException as e:
            error_msg = f"ASR API request timeout: {str(e)}"
            logger.error(
                error_msg,
                exc_info=True,
                extra={"timestamp": logger.makeRecord(
                    logger.name, logging.ERROR, "", 0, error_msg, (), None
                ).created}
            )
            raise ASRServiceError("语音识别服务不可用: 请求超时")
            
        except httpx.RequestError as e:
            error_msg = f"ASR API request failed: {str(e)}"
            logger.error(
                error_msg,
                exc_info=True,
                extra={"timestamp": logger.makeRecord(
                    logger.name, logging.ERROR, "", 0, error_msg, (), None
                ).created}
            )
            raise ASRServiceError(f"语音识别服务不可用: 网络错误")
            
        except Exception as e:
            error_msg = f"Unexpected error in ASR service: {str(e)}"
            logger.error(
                error_msg,
                exc_info=True,
                extra={"timestamp": logger.makeRecord(
                    logger.name, logging.ERROR, "", 0, error_msg, (), None
                ).created}
            )
            raise ASRServiceError(f"语音识别服务不可用: {str(e)}")
