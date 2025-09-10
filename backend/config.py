import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    """Configuration settings for the RAG system"""
    # Anthropic API settings
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    
    # DeepSeek API settings - 双模型路由策略
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://llm.chutes.ai/v1")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "deepseek")
    
    # 双模型配置
    MODEL_REASON: str = os.getenv("MODEL_REASON", "deepseek-ai/DeepSeek-R1")
    MODEL_TOOLCALL: str = os.getenv("MODEL_TOOLCALL", "deepseek-ai/DeepSeek-V3")
    
    # 支持工具调用的模型集合
    TOOLCALL_MODELS: set = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.TOOLCALL_MODELS is None:
            self.TOOLCALL_MODELS = {
                "deepseek-ai/DeepSeek-V3",
                "deepseek-ai/DeepSeek-Chat", 
                "deepseek-ai/DeepSeek-V3-0324"
            }
    
    # Embedding model settings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Document processing settings
    CHUNK_SIZE: int = 800       # Size of text chunks for vector storage
    CHUNK_OVERLAP: int = 100     # Characters to overlap between chunks
    MAX_RESULTS: int = 5         # Maximum search results to return
    MAX_HISTORY: int = 2         # Number of conversation messages to remember
    
    # Database paths
    CHROMA_PATH: str = "./chroma_db"  # ChromaDB storage location

config = Config()


