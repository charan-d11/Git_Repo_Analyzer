from langchain_groq import ChatGroq
from app.config.config import GROQ_API_KEY
from app.common.coustume_exception import CustomException
from app.common.logger import get_logger

logger=get_logger(__name__)

def load_llm(model_name:str="openai/gpt-oss-120b",groq_api_key:str=GROQ_API_KEY):
    try:
        logger.info("Loading Your Model...")
        llm=ChatGroq(
            model_name=model_name,
            groq_api_key=groq_api_key,
            max_tokens=500,
            temperature=0.8
        )
        logger.info("LLM Model IS Loaded Successfully.")
        return llm
    except Exception as e:
        error_message=CustomException("Unable To Load The LLM Model.")
        logger.error(str(error_message))
        return None