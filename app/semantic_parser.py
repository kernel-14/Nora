"""Semantic Parser service for Voice Text Processor.

This module implements the SemanticParserService class for parsing text
into structured data (mood, inspirations, todos) using the GLM-4-Flash API.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 9.2, 9.5
"""

import logging
import json
from typing import Optional
import httpx

from app.models import ParsedData, MoodData, InspirationData, TodoData


logger = logging.getLogger(__name__)


class SemanticParserError(Exception):
    """Exception raised when semantic parsing operations fail.
    
    This exception is raised when the GLM-4-Flash API call fails,
    such as due to network issues, API errors, or invalid responses.
    
    Requirements: 3.5
    """
    
    def __init__(self, message: str = "语义解析服务不可用"):
        """Initialize SemanticParserError.
        
        Args:
            message: Error message describing the failure
        """
        super().__init__(message)
        self.message = message


class SemanticParserService:
    """Service for parsing text into structured data using GLM-4-Flash API.
    
    This service handles semantic parsing by calling the GLM-4-Flash API
    to extract mood, inspirations, and todos from text. It manages API
    authentication, request formatting, response parsing, and error handling.
    
    Attributes:
        api_key: Zhipu AI API key for authentication
        client: Async HTTP client for making API requests
        api_url: GLM-4-Flash API endpoint URL
        model: Model identifier
        system_prompt: System prompt for data conversion
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 9.2, 9.5
    """
    
    def __init__(self, api_key: str):
        """Initialize the semantic parser service.
        
        Args:
            api_key: Zhipu AI API key for authentication
        
        Requirements: 3.1, 3.2
        """
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.model = "glm-4-flash"
        
        # System prompt as specified in requirements
        self.system_prompt = (
            "你是一个专业的文本语义分析助手。请将用户输入的文本解析为结构化的 JSON 数据。\n\n"
            "你需要提取以下三个维度的信息：\n\n"
            "1. **情绪 (mood)**：\n"
            "   - type: 情绪类型（如：喜悦、焦虑、平静、忧虑、兴奋、悲伤等中文词汇）\n"
            "   - intensity: 情绪强度（1-10的整数，10表示最强烈）\n"
            "   - keywords: 情绪关键词列表（3-5个中文词）\n\n"
            "2. **灵感 (inspirations)**：数组，每个元素包含：\n"
            "   - core_idea: 核心观点或想法（20字以内的中文）\n"
            "   - tags: 相关标签列表（3-5个中文词）\n"
            "   - category: 所属分类（必须是：工作、生活、学习、创意 之一）\n\n"
            "3. **待办 (todos)**：数组，每个元素包含：\n"
            "   - task: 任务描述（中文）\n"
            "   - time: 时间信息（如：明天、下周、周五等，如果没有则为null）\n"
            "   - location: 地点信息（如果没有则为null）\n"
            "   - status: 状态（默认为\"pending\"）\n\n"
            "**重要规则**：\n"
            "- 如果文本中没有某个维度的信息，mood 返回 null，inspirations 和 todos 返回空数组 []\n"
            "- 必须返回有效的 JSON 格式，不要添加任何其他说明文字\n"
            "- 所有字段名使用英文，内容使用中文\n"
            "- 直接返回 JSON，不要用 markdown 代码块包裹\n\n"
            "返回格式示例：\n"
            "{\n"
            "  \"mood\": {\"type\": \"焦虑\", \"intensity\": 7, \"keywords\": [\"压力\", \"疲惫\", \"放松\"]},\n"
            "  \"inspirations\": [{\"core_idea\": \"晚霞可以缓解压力\", \"tags\": [\"自然\", \"治愈\"], \"category\": \"生活\"}],\n"
            "  \"todos\": [{\"task\": \"整理文档\", \"time\": \"明天\", \"location\": null, \"status\": \"pending\"}]\n"
            "}"
        )
    
    async def close(self):
        """Close the HTTP client.
        
        This should be called when the service is no longer needed
        to properly clean up resources.
        """
        await self.client.aclose()
    
    async def parse(self, text: str) -> ParsedData:
        """Parse text into structured data using GLM-4-Flash API.
        
        This method sends the text to the GLM-4-Flash API with the configured
        system prompt and returns structured data containing mood, inspirations,
        and todos. It handles API errors, missing dimensions, and logs all errors
        with timestamps and stack traces.
        
        Args:
            text: Text content to parse
        
        Returns:
            ParsedData object containing mood (optional), inspirations (list),
            and todos (list). Missing dimensions return null or empty arrays.
        
        Raises:
            SemanticParserError: If API call fails or returns invalid response
        
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 9.2, 9.5
        """
        try:
            # Prepare request headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            logger.info(f"Calling GLM-4-Flash API for semantic parsing. Text length: {len(text)}")
            
            # Make API request
            response = await self.client.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            # Check response status
            if response.status_code != 200:
                error_msg = f"GLM-4-Flash API returned status {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f": {error_detail}"
                except Exception:
                    error_msg += f": {response.text}"
                
                logger.error(
                    f"Semantic parsing API call failed: {error_msg}",
                    exc_info=True,
                    extra={"timestamp": logger.makeRecord(
                        logger.name, logging.ERROR, "", 0, error_msg, (), None
                    ).created}
                )
                raise SemanticParserError(f"语义解析服务不可用: {error_msg}")
            
            # Parse response
            try:
                result = response.json()
            except Exception as e:
                error_msg = f"Failed to parse GLM-4-Flash API response: {str(e)}"
                logger.error(
                    error_msg,
                    exc_info=True,
                    extra={"timestamp": logger.makeRecord(
                        logger.name, logging.ERROR, "", 0, error_msg, (), None
                    ).created}
                )
                raise SemanticParserError(f"语义解析服务不可用: 响应格式无效")
            
            # Extract content from response
            try:
                content = result["choices"][0]["message"]["content"]
            except (KeyError, IndexError) as e:
                error_msg = f"Invalid API response structure: {str(e)}"
                logger.error(
                    error_msg,
                    exc_info=True,
                    extra={"timestamp": logger.makeRecord(
                        logger.name, logging.ERROR, "", 0, error_msg, (), None
                    ).created}
                )
                raise SemanticParserError(f"语义解析服务不可用: 响应结构无效")
            
            # Parse JSON from content
            try:
                # Try to extract JSON from markdown code blocks if present
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                elif "```" in content:
                    json_start = content.find("```") + 3
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                
                parsed_json = json.loads(content)
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse JSON from API response: {str(e)}"
                logger.error(
                    error_msg,
                    exc_info=True,
                    extra={"timestamp": logger.makeRecord(
                        logger.name, logging.ERROR, "", 0, error_msg, (), None
                    ).created}
                )
                raise SemanticParserError(f"语义解析服务不可用: JSON 解析失败")
            
            # Extract and validate mood data
            mood = None
            if "mood" in parsed_json and parsed_json["mood"]:
                try:
                    mood_data = parsed_json["mood"]
                    if isinstance(mood_data, dict):
                        mood = MoodData(
                            type=mood_data.get("type"),
                            intensity=mood_data.get("intensity"),
                            keywords=mood_data.get("keywords", [])
                        )
                except Exception as e:
                    logger.warning(f"Failed to parse mood data: {str(e)}")
                    mood = None
            
            # Extract and validate inspirations
            inspirations = []
            if "inspirations" in parsed_json and parsed_json["inspirations"]:
                for insp_data in parsed_json["inspirations"]:
                    try:
                        if isinstance(insp_data, dict):
                            inspiration = InspirationData(
                                core_idea=insp_data.get("core_idea", ""),
                                tags=insp_data.get("tags", []),
                                category=insp_data.get("category", "生活")
                            )
                            inspirations.append(inspiration)
                    except Exception as e:
                        logger.warning(f"Failed to parse inspiration data: {str(e)}")
                        continue
            
            # Extract and validate todos
            todos = []
            if "todos" in parsed_json and parsed_json["todos"]:
                for todo_data in parsed_json["todos"]:
                    try:
                        if isinstance(todo_data, dict):
                            todo = TodoData(
                                task=todo_data.get("task", ""),
                                time=todo_data.get("time"),
                                location=todo_data.get("location"),
                                status=todo_data.get("status", "pending")
                            )
                            todos.append(todo)
                    except Exception as e:
                        logger.warning(f"Failed to parse todo data: {str(e)}")
                        continue
            
            logger.info(
                f"Semantic parsing successful. "
                f"Mood: {'present' if mood else 'none'}, "
                f"Inspirations: {len(inspirations)}, "
                f"Todos: {len(todos)}"
            )
            
            return ParsedData(
                mood=mood,
                inspirations=inspirations,
                todos=todos
            )
            
        except SemanticParserError:
            # Re-raise SemanticParserError as-is
            raise
            
        except httpx.TimeoutException as e:
            error_msg = f"GLM-4-Flash API request timeout: {str(e)}"
            logger.error(
                error_msg,
                exc_info=True,
                extra={"timestamp": logger.makeRecord(
                    logger.name, logging.ERROR, "", 0, error_msg, (), None
                ).created}
            )
            raise SemanticParserError("语义解析服务不可用: 请求超时")
            
        except httpx.RequestError as e:
            error_msg = f"GLM-4-Flash API request failed: {str(e)}"
            logger.error(
                error_msg,
                exc_info=True,
                extra={"timestamp": logger.makeRecord(
                    logger.name, logging.ERROR, "", 0, error_msg, (), None
                ).created}
            )
            raise SemanticParserError(f"语义解析服务不可用: 网络错误")
            
        except Exception as e:
            error_msg = f"Unexpected error in semantic parser service: {str(e)}"
            logger.error(
                error_msg,
                exc_info=True,
                extra={"timestamp": logger.makeRecord(
                    logger.name, logging.ERROR, "", 0, error_msg, (), None
                ).created}
            )
            raise SemanticParserError(f"语义解析服务不可用: {str(e)}")
