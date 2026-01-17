"""Main FastAPI application for Voice Text Processor.

This module initializes the FastAPI application, sets up configuration,
logging, and defines the application lifecycle.

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse

from app.config import init_config, get_config
from app.logging_config import setup_logging, set_request_id, clear_request_id
from app.models import ProcessResponse, RecordData, ParsedData
from app.storage import StorageService, StorageError
from app.asr_service import ASRService, ASRServiceError
from app.semantic_parser import SemanticParserService, SemanticParserError


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.
    
    This handles startup and shutdown events for the application.
    On startup, it initializes configuration and logging.
    
    Requirements: 10.4 - Startup configuration validation
    """
    # Startup
    logger.info("Starting Voice Text Processor application...")
    
    try:
        # Initialize configuration (will raise ValueError if invalid)
        config = init_config()
        logger.info("Configuration loaded and validated successfully")
        
        # Setup logging with config values
        setup_logging(
            log_level=config.log_level,
            log_file=config.log_file
        )
        logger.info("Logging system configured")
        
        # Log configuration (without sensitive data)
        logger.info(f"Data directory: {config.data_dir}")
        logger.info(f"Max audio size: {config.max_audio_size} bytes")
        logger.info(f"Log level: {config.log_level}")
        
    except ValueError as e:
        # Configuration validation failed - refuse to start
        logger.error(f"Configuration validation failed: {e}")
        logger.error("Application startup aborted due to configuration errors")
        raise RuntimeError(f"Configuration error: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error during startup: {e}", exc_info=True)
        raise RuntimeError(f"Startup error: {e}") from e
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Voice Text Processor application...")
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Voice Text Processor",
    description="治愈系记录助手后端核心模块 - 语音和文本处理服务",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "service": "Voice Text Processor",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        config = get_config()
        return {
            "status": "healthy",
            "data_dir": str(config.data_dir),
            "max_audio_size": config.max_audio_size
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# Validation error class
class ValidationError(Exception):
    """Exception raised when input validation fails.
    
    Requirements: 1.3, 8.5, 9.1
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


# Supported audio formats
SUPPORTED_AUDIO_FORMATS = {".mp3", ".wav", ".m4a"}


@app.post("/api/process", response_model=ProcessResponse)
async def process_input(
    audio: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
) -> ProcessResponse:
    """Process user input (audio or text) and extract structured data.
    
    This endpoint accepts either an audio file or text content, performs
    speech recognition (if audio), semantic parsing, and stores the results.
    
    Args:
        audio: Audio file (multipart/form-data) in mp3, wav, or m4a format
        text: Text content (application/json) in UTF-8 encoding
    
    Returns:
        ProcessResponse containing record_id, timestamp, mood, inspirations, todos
    
    Raises:
        HTTPException: With appropriate status code and error message
    
    Requirements: 1.1, 1.2, 1.3, 7.7, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 9.1, 9.2, 9.3, 9.4, 9.5
    """
    request_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Set request_id in logging context
    set_request_id(request_id)
    
    logger.info(f"Processing request - audio: {audio is not None}, text: {text is not None}")
    
    try:
        # Input validation
        if audio is None and text is None:
            raise ValidationError("请提供音频文件或文本内容")
        
        if audio is not None and text is not None:
            raise ValidationError("请只提供音频文件或文本内容中的一种")
        
        # Get configuration
        config = get_config()
        
        # Initialize services
        storage_service = StorageService(str(config.data_dir))
        asr_service = ASRService(config.zhipu_api_key)
        parser_service = SemanticParserService(config.zhipu_api_key)
        
        original_text = ""
        input_type = "text"
        
        try:
            # Handle audio input
            if audio is not None:
                input_type = "audio"
                
                # Validate audio format
                filename = audio.filename or "audio"
                file_ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
                
                if file_ext not in SUPPORTED_AUDIO_FORMATS:
                    raise ValidationError(
                        f"不支持的音频格式: {file_ext}. "
                        f"支持的格式: {', '.join(SUPPORTED_AUDIO_FORMATS)}"
                    )
                
                # Read audio file
                audio_content = await audio.read()
                
                # Validate audio file size
                if len(audio_content) > config.max_audio_size:
                    raise ValidationError(
                        f"音频文件过大: {len(audio_content)} bytes. "
                        f"最大允许: {config.max_audio_size} bytes"
                    )
                
                logger.info(
                    f"Audio file received: {filename}, "
                    f"size: {len(audio_content)} bytes"
                )
                
                # Transcribe audio to text
                try:
                    original_text = await asr_service.transcribe(audio_content, filename)
                    logger.info(
                        f"ASR transcription successful. "
                        f"Text length: {len(original_text)}"
                    )
                except ASRServiceError as e:
                    logger.error(
                        f"ASR service error: {e.message}",
                        exc_info=True
                    )
                    raise
            
            # Handle text input
            else:
                # Validate text encoding (UTF-8)
                # Accept whitespace-only text as valid UTF-8, but reject None or empty string
                if text is None or text == "":
                    raise ValidationError("文本内容不能为空")
                
                original_text = text
                logger.info(
                    f"Text input received. "
                    f"Length: {len(original_text)}"
                )
            
            # Perform semantic parsing
            try:
                parsed_data = await parser_service.parse(original_text)
                logger.info(
                    f"Semantic parsing successful. "
                    f"Mood: {'present' if parsed_data.mood else 'none'}, "
                    f"Inspirations: {len(parsed_data.inspirations)}, "
                    f"Todos: {len(parsed_data.todos)}"
                )
            except SemanticParserError as e:
                logger.error(
                    f"Semantic parser error: {e.message}",
                    exc_info=True
                )
                raise
            
            # Generate record ID and timestamp
            record_id = str(uuid.uuid4())
            record_timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Create record data
            record = RecordData(
                record_id=record_id,
                timestamp=record_timestamp,
                input_type=input_type,
                original_text=original_text,
                parsed_data=parsed_data
            )
            
            # Save to storage
            try:
                storage_service.save_record(record)
                logger.info(f"Record saved: {record_id}")
                
                # Save mood if present
                if parsed_data.mood:
                    storage_service.append_mood(
                        parsed_data.mood,
                        record_id,
                        record_timestamp
                    )
                    logger.info(f"Mood data saved")
                
                # Save inspirations if present
                if parsed_data.inspirations:
                    storage_service.append_inspirations(
                        parsed_data.inspirations,
                        record_id,
                        record_timestamp
                    )
                    logger.info(
                        f"{len(parsed_data.inspirations)} "
                        f"inspiration(s) saved"
                    )
                
                # Save todos if present
                if parsed_data.todos:
                    storage_service.append_todos(
                        parsed_data.todos,
                        record_id,
                        record_timestamp
                    )
                    logger.info(
                        f"{len(parsed_data.todos)} "
                        f"todo(s) saved"
                    )
                
            except StorageError as e:
                logger.error(
                    f"Storage error: {str(e)}",
                    exc_info=True
                )
                raise
            
            # Build success response
            response = ProcessResponse(
                record_id=record_id,
                timestamp=record_timestamp,
                mood=parsed_data.mood,
                inspirations=parsed_data.inspirations,
                todos=parsed_data.todos
            )
            
            logger.info(f"Request processed successfully")
            
            return response
        
        finally:
            # Clean up services
            await asr_service.close()
            await parser_service.close()
            # Clear request_id from context
            clear_request_id()
    
    except ValidationError as e:
        # Input validation error - HTTP 400
        logger.warning(
            f"Validation error: {e.message}",
            exc_info=True
        )
        clear_request_id()
        return JSONResponse(
            status_code=400,
            content={
                "error": e.message,
                "timestamp": timestamp
            }
        )
    
    except ASRServiceError as e:
        # ASR service error - HTTP 500
        logger.error(
            f"ASR service unavailable: {e.message}",
            exc_info=True
        )
        clear_request_id()
        return JSONResponse(
            status_code=500,
            content={
                "error": "语音识别服务不可用",
                "detail": e.message,
                "timestamp": timestamp
            }
        )
    
    except SemanticParserError as e:
        # Semantic parser error - HTTP 500
        logger.error(
            f"Semantic parser unavailable: {e.message}",
            exc_info=True
        )
        clear_request_id()
        return JSONResponse(
            status_code=500,
            content={
                "error": "语义解析服务不可用",
                "detail": e.message,
                "timestamp": timestamp
            }
        )
    
    except StorageError as e:
        # Storage error - HTTP 500
        logger.error(
            f"Storage error: {str(e)}",
            exc_info=True
        )
        clear_request_id()
        return JSONResponse(
            status_code=500,
            content={
                "error": "数据存储失败",
                "detail": str(e),
                "timestamp": timestamp
            }
        )
    
    except Exception as e:
        # Unexpected error - HTTP 500
        logger.error(
            f"Unexpected error: {str(e)}",
            exc_info=True
        )
        clear_request_id()
        return JSONResponse(
            status_code=500,
            content={
                "error": "服务器内部错误",
                "detail": str(e),
                "timestamp": timestamp
            }
        )


if __name__ == "__main__":
    import uvicorn
    
    # Load config for server settings
    try:
        config = init_config()
        setup_logging(log_level=config.log_level, log_file=config.log_file)
        
        # Run server
        uvicorn.run(
            "app.main:app",
            host=config.host,
            port=config.port,
            reload=False,
            log_level=config.log_level.lower()
        )
    except Exception as e:
        print(f"Failed to start application: {e}")
        exit(1)
