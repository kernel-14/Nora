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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://172.18.16.245:5173",  # 允许从电脑 IP 访问
        "*"  # 开发环境允许所有来源（生产环境应该限制）
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for generated images
from pathlib import Path
generated_images_dir = Path("generated_images")
generated_images_dir.mkdir(exist_ok=True)
app.mount("/generated_images", StaticFiles(directory="generated_images"), name="generated_images")


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
SUPPORTED_AUDIO_FORMATS = {".mp3", ".wav", ".m4a", ".webm"}


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


@app.get("/api/records")
async def get_records():
    """Get all records."""
    try:
        config = get_config()
        storage_service = StorageService(str(config.data_dir))
        records = storage_service._read_json_file(storage_service.records_file)
        return {"records": records}
    except Exception as e:
        logger.error(f"Failed to get records: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/moods")
async def get_moods():
    """Get all moods from both moods.json and records.json."""
    try:
        config = get_config()
        storage_service = StorageService(str(config.data_dir))
        
        # 1. 读取 moods.json
        moods_from_file = storage_service._read_json_file(storage_service.moods_file)
        logger.info(f"Loaded {len(moods_from_file)} moods from moods.json")
        
        # 2. 从 records.json 中提取心情数据
        records = storage_service._read_json_file(storage_service.records_file)
        moods_from_records = []
        
        for record in records:
            # 检查 parsed_data 中是否有 mood
            parsed_data = record.get("parsed_data", {})
            mood_data = parsed_data.get("mood")
            
            if mood_data and mood_data.get("type"):
                # 构造心情对象
                mood_obj = {
                    "record_id": record["record_id"],
                    "timestamp": record["timestamp"],
                    "type": mood_data.get("type"),
                    "intensity": mood_data.get("intensity", 5),
                    "keywords": mood_data.get("keywords", [])
                }
                moods_from_records.append(mood_obj)
        
        logger.info(f"Extracted {len(moods_from_records)} moods from records.json")
        
        # 3. 合并两个来源的心情数据（去重，优先使用 records 中的数据）
        mood_dict = {}
        
        # 先添加 moods.json 中的数据
        for mood in moods_from_file:
            mood_dict[mood["record_id"]] = mood
        
        # 再添加/覆盖 records.json 中的数据
        for mood in moods_from_records:
            mood_dict[mood["record_id"]] = mood
        
        # 转换为列表并按时间排序（最新的在前）
        all_moods = list(mood_dict.values())
        all_moods.sort(key=lambda x: x["timestamp"], reverse=True)
        
        logger.info(f"Total unique moods: {len(all_moods)}")
        
        return {"moods": all_moods}
    except Exception as e:
        logger.error(f"Failed to get moods: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/inspirations")
async def get_inspirations():
    """Get all inspirations."""
    try:
        config = get_config()
        storage_service = StorageService(str(config.data_dir))
        inspirations = storage_service._read_json_file(storage_service.inspirations_file)
        return {"inspirations": inspirations}
    except Exception as e:
        logger.error(f"Failed to get inspirations: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/todos")
async def get_todos():
    """Get all todos."""
    try:
        config = get_config()
        storage_service = StorageService(str(config.data_dir))
        todos = storage_service._read_json_file(storage_service.todos_file)
        return {"todos": todos}
    except Exception as e:
        logger.error(f"Failed to get todos: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.patch("/api/todos/{todo_id}")
async def update_todo(todo_id: str, status: str = Form(...)):
    """Update todo status."""
    try:
        config = get_config()
        storage_service = StorageService(str(config.data_dir))
        todos = storage_service._read_json_file(storage_service.todos_file)
        
        # Find and update todo
        updated = False
        for todo in todos:
            if todo.get("record_id") == todo_id or str(hash(todo.get("task", ""))) == todo_id:
                todo["status"] = status
                updated = True
                break
        
        if not updated:
            return JSONResponse(
                status_code=404,
                content={"error": "Todo not found"}
            )
        
        storage_service._write_json_file(storage_service.todos_file, todos)
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to update todo: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/api/chat")
async def chat_with_ai(text: str = Form(...)):
    """Chat with AI assistant using RAG with records.json as knowledge base.
    
    This endpoint provides conversational AI that has context about the user's
    previous records, moods, inspirations, and todos.
    """
    try:
        config = get_config()
        storage_service = StorageService(str(config.data_dir))
        
        # Load user's records as RAG knowledge base
        records = storage_service._read_json_file(storage_service.records_file)
        
        # Build context from recent records (last 10)
        recent_records = records[-10:] if len(records) > 10 else records
        context_parts = []
        
        for record in recent_records:
            original_text = record.get('original_text', '')
            timestamp = record.get('timestamp', '')
            
            # Add parsed data context
            parsed_data = record.get('parsed_data', {})
            mood = parsed_data.get('mood')
            inspirations = parsed_data.get('inspirations', [])
            todos = parsed_data.get('todos', [])
            
            context_entry = f"[{timestamp}] 用户说: {original_text}"
            
            if mood:
                context_entry += f"\n情绪: {mood.get('type')} (强度: {mood.get('intensity')})"
            
            if inspirations:
                ideas = [insp.get('core_idea') for insp in inspirations]
                context_entry += f"\n灵感: {', '.join(ideas)}"
            
            if todos:
                tasks = [todo.get('task') for todo in todos]
                context_entry += f"\n待办: {', '.join(tasks)}"
            
            context_parts.append(context_entry)
        
        # Build system prompt with context
        context_text = "\n\n".join(context_parts) if context_parts else "暂无历史记录"
        
        system_prompt = f"""你是一个温柔、善解人意的AI陪伴助手。你的名字叫小喵。
你会用温暖、治愈的语气和用户聊天，给予他们情感支持和陪伴。
回复要简短、自然、有温度。

你可以参考用户的历史记录来提供更贴心的回复：

{context_text}

请基于这些背景信息，用温暖、理解的语气回复用户。如果用户提到之前的事情，你可以自然地关联起来。"""
        
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                    headers={
                        "Authorization": f"Bearer {config.zhipu_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "glm-4-flash",
                        "messages": [
                            {
                                "role": "system",
                                "content": system_prompt
                            },
                            {
                                "role": "user",
                                "content": text
                            }
                        ],
                        "temperature": 0.8,
                        "top_p": 0.9
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    logger.info(f"AI chat successful with RAG context")
                    return {"response": ai_response}
                else:
                    logger.error(f"AI chat failed: {response.status_code} {response.text}")
                    return {"response": "抱歉，我现在有点累了，稍后再聊好吗？"}
        
        except Exception as e:
            logger.error(f"AI API call error: {e}")
            return {"response": "抱歉，我现在有点累了，稍后再聊好吗？"}
            
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {"response": "抱歉，我现在有点累了，稍后再聊好吗？"}


@app.get("/api/user/config")
async def get_user_config():
    """Get user configuration including character image."""
    try:
        from app.user_config import UserConfig
        from pathlib import Path
        import os
        
        config = get_config()
        user_config = UserConfig(str(config.data_dir))
        user_data = user_config.load_config()
        
        # 如果没有保存的图片，尝试加载最新的本地图片
        if not user_data.get('character', {}).get('image_url'):
            generated_images_dir = Path("generated_images")
            if generated_images_dir.exists():
                # 获取所有图片文件
                image_files = list(generated_images_dir.glob("character_*.jpeg"))
                if image_files:
                    # 按修改时间排序，获取最新的
                    latest_image = max(image_files, key=lambda p: p.stat().st_mtime)
                    
                    # 构建 URL 路径
                    image_url = f"http://localhost:8000/generated_images/{latest_image.name}"
                    
                    # 从文件名提取偏好设置
                    # 格式: character_颜色_性格_时间戳.jpeg
                    parts = latest_image.stem.split('_')
                    if len(parts) >= 3:
                        color = parts[1]
                        personality = parts[2]
                        
                        # 更新配置
                        user_config.save_character_image(
                            image_url=str(latest_image),
                            prompt=f"Character with {color} and {personality}",
                            preferences={
                                "color": color,
                                "personality": personality,
                                "appearance": "无配饰",
                                "role": "陪伴式朋友"
                            }
                        )
                        
                        # 重新加载配置
                        user_data = user_config.load_config()
                        
                        logger.info(f"Loaded latest local image: {latest_image.name}")
        
        # 如果 image_url 是本地路径，转换为 URL
        image_url = user_data.get('character', {}).get('image_url')
        if image_url and not image_url.startswith('http'):
            # 本地路径，转换为 URL（处理 Windows 和 Unix 路径）
            image_path = Path(image_url)
            if image_path.exists():
                # 使用正斜杠构建 URL
                user_data['character']['image_url'] = f"http://localhost:8000/generated_images/{image_path.name}"
            else:
                # 如果路径不存在，尝试只使用文件名
                filename = image_path.name
                full_path = Path("generated_images") / filename
                if full_path.exists():
                    user_data['character']['image_url'] = f"http://localhost:8000/generated_images/{filename}"
                    logger.info(f"Converted path to URL: {filename}")
        
        return user_data
    except Exception as e:
        logger.error(f"Failed to get user config: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/api/character/generate")
async def generate_character(
    color: str = Form(...),
    personality: str = Form(...),
    appearance: str = Form(...),
    role: str = Form(...)
):
    """Generate AI character image based on preferences.
    
    Args:
        color: Color preference (温暖粉/天空蓝/薄荷绿等)
        personality: Personality trait (活泼/温柔/聪明等)
        appearance: Appearance feature (戴眼镜/戴帽子等)
        role: Character role (陪伴式朋友/温柔照顾型长辈等)
    
    Returns:
        JSON with image_url, prompt, and preferences
    """
    try:
        from app.image_service import ImageGenerationService, ImageGenerationError
        from app.user_config import UserConfig
        from datetime import datetime
        from pathlib import Path
        import httpx
        
        config = get_config()
        
        # 检查是否配置了 MiniMax API
        minimax_api_key = getattr(config, 'minimax_api_key', None)
        
        if not minimax_api_key:
            logger.warning("MiniMax API key not configured")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "MiniMax API 未配置",
                    "detail": "请在 .env 文件中配置 MINIMAX_API_KEY。访问 https://platform.minimaxi.com/ 获取 API 密钥。"
                }
            )
        
        # 初始化服务
        image_service = ImageGenerationService(
            api_key=minimax_api_key,
            group_id=getattr(config, 'minimax_group_id', None)
        )
        user_config = UserConfig(str(config.data_dir))
        
        try:
            logger.info(
                f"Generating character image: "
                f"color={color}, personality={personality}, "
                f"appearance={appearance}, role={role}"
            )
            
            # 生成图像
            result = await image_service.generate_image(
                color=color,
                personality=personality,
                appearance=appearance,
                role=role,
                aspect_ratio="1:1",
                n=1
            )
            
            # 下载图片到本地
            generated_images_dir = Path("generated_images")
            generated_images_dir.mkdir(exist_ok=True)
            
            # 生成文件名：character_颜色_性格_时间戳.jpeg
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"character_{color}_{personality}_{timestamp}.jpeg"
            local_path = generated_images_dir / filename
            
            logger.info(f"Downloading image to: {local_path}")
            
            # 下载图片
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(result['url'])
                if response.status_code == 200:
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"Image saved to: {local_path}")
                else:
                    logger.error(f"Failed to download image: HTTP {response.status_code}")
                    # 如果下载失败，仍然使用远程 URL
                    local_path = None
            
            # 保存到用户配置
            preferences = {
                "color": color,
                "personality": personality,
                "appearance": appearance,
                "role": role
            }
            
            # 使用本地路径（如果下载成功）
            image_url = str(local_path) if local_path else result['url']
            
            user_config.save_character_image(
                image_url=image_url,
                prompt=result['prompt'],
                revised_prompt=result.get('metadata', {}).get('revised_prompt'),
                preferences=preferences
            )
            
            logger.info(f"Character image generated and saved: {image_url}")
            
            return {
                "success": True,
                "image_url": image_url,
                "prompt": result['prompt'],
                "preferences": preferences,
                "task_id": result.get('task_id')
            }
        
        finally:
            await image_service.close()
    
    except ImageGenerationError as e:
        logger.error(f"Image generation error: {e.message}")
        
        # 提供更友好的错误信息
        error_detail = e.message
        if "invalid api key" in e.message.lower():
            error_detail = "API 密钥无效，请检查 MINIMAX_API_KEY 配置是否正确"
        elif "quota" in e.message.lower() or "配额" in e.message:
            error_detail = "API 配额不足，请充值或等待配额恢复"
        elif "timeout" in e.message.lower() or "超时" in e.message:
            error_detail = "请求超时，请检查网络连接后重试"
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "图像生成失败",
                "detail": error_detail
            }
        )
    
    except Exception as e:
        logger.error(f"Failed to generate character: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "生成角色形象失败",
                "detail": str(e)
            }
        )


@app.get("/api/character/history")
async def get_character_history():
    """Get list of all generated character images.
    
    Returns:
        JSON with list of historical character images
    """
    try:
        from pathlib import Path
        import os
        
        generated_images_dir = Path("generated_images")
        
        if not generated_images_dir.exists():
            return {"images": []}
        
        # 获取所有图片文件
        image_files = []
        for file in generated_images_dir.glob("character_*.jpeg"):
            # 解析文件名：character_颜色_性格_时间戳.jpeg
            parts = file.stem.split("_")
            if len(parts) >= 4:
                color = parts[1]
                personality = parts[2]
                timestamp = "_".join(parts[3:])
                
                # 获取文件信息
                stat = file.stat()
                
                image_files.append({
                    "filename": file.name,
                    "url": f"http://localhost:8000/generated_images/{file.name}",
                    "color": color,
                    "personality": personality,
                    "timestamp": timestamp,
                    "created_at": stat.st_ctime,
                    "size": stat.st_size
                })
        
        # 按创建时间倒序排列（最新的在前）
        image_files.sort(key=lambda x: x["created_at"], reverse=True)
        
        logger.info(f"Found {len(image_files)} historical character images")
        
        return {"images": image_files}
        
    except Exception as e:
        logger.error(f"Error getting character history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/character/select")
async def select_character(
    filename: str = Form(...)
):
    """Select a historical character image as current.
    
    Args:
        filename: Filename of the character image to select
    
    Returns:
        JSON with success status and image URL
    """
    try:
        from app.user_config import UserConfig
        from pathlib import Path
        
        config = get_config()
        user_config = UserConfig(str(config.data_dir))
        
        # 验证文件存在
        image_path = Path("generated_images") / filename
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="图片文件不存在")
        
        # 解析文件名获取偏好设置
        parts = filename.replace(".jpeg", "").split("_")
        if len(parts) >= 4:
            color = parts[1]
            personality = parts[2]
            
            preferences = {
                "color": color,
                "personality": personality,
                "appearance": "未知",
                "role": "未知"
            }
        else:
            preferences = {}
        
        # 更新用户配置
        image_url = str(image_path)
        user_config.save_character_image(
            image_url=image_url,
            prompt=f"历史形象: {filename}",
            preferences=preferences
        )
        
        logger.info(f"Selected historical character: {filename}")
        
        # 返回 HTTP URL
        http_url = f"http://localhost:8000/generated_images/{filename}"
        
        return {
            "success": True,
            "image_url": http_url,
            "filename": filename,
            "preferences": preferences
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error selecting character: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/character/preferences")
async def update_character_preferences(
    color: Optional[str] = Form(None),
    personality: Optional[str] = Form(None),
    appearance: Optional[str] = Form(None),
    role: Optional[str] = Form(None)
):
    """Update character preferences without generating new image.
    
    Args:
        color: Color preference (optional)
        personality: Personality trait (optional)
        appearance: Appearance feature (optional)
        role: Character role (optional)
    
    Returns:
        JSON with updated preferences
    """
    try:
        from app.user_config import UserConfig
        
        config = get_config()
        user_config = UserConfig(str(config.data_dir))
        
        # 更新偏好设置
        user_config.update_character_preferences(
            color=color,
            personality=personality,
            appearance=appearance,
            role=role
        )
        
        # 返回更新后的配置
        updated_config = user_config.load_config()
        
        return {
            "success": True,
            "preferences": updated_config['character']['preferences']
        }
    
    except Exception as e:
        logger.error(f"Failed to update preferences: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
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
