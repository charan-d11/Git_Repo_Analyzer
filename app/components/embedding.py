from langchain_huggingface import HuggingFaceEmbeddings
from app.common.logger import get_logger
from app.common.coustume_exception import CustomException

logger=get_logger(__name__)

def get_embeddings():
    try:
        logger.info("Embedding Model is loading.")
        model=HuggingFaceEmbeddings(
            model_name='sentence-transformers/all-MiniLM-L6-v2',
            model_kwargs={"device":"cpu"}
        )
        logger.info("HuggingFace Embeddeding layer load successfully...")
        return model
    except Exception as e:
        error_message=CustomException("unable to load HuggingFace Embeddeding layer!",e)
        logger.error(str(error_message))
        raise error_message 