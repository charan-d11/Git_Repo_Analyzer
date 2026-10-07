from app.common.logger import get_logger
from app.common.coustume_exception import CustomException
from app.components.embedding import get_embeddings
import os
from langchain_community.vectorstores import FAISS
from app.config.config import FAISS_INDEX_PATH

logger=get_logger(__name__)

def load_vector():
    try:
        embedding_model=get_embeddings()
        if os.path.exists(FAISS_INDEX_PATH):
            logger.info("LOAD EXISTING FAISS VECTOR STORE")
            return FAISS.load_local(FAISS_INDEX_PATH,embedding_model,allow_dangerous_deserialization=True)
        else:
            logger.warning("NO DATA BASE PATH IS FOUND")
    except Exception as e:
        error_message=CustomException("UNABLE TO LOAD VECTOR DATA BASE")
        logger.error(str(error_message))
        raise error_message

def save_vector(chunks):
    try:
        if not chunks:
            raise CustomException("No Chunks Are Found!")
        logger.info("SAVE YOUR NEW VECTOR")
        embedding_model=get_embeddings()

        vector_store=FAISS.from_documents(chunks,embedding_model)
        logger.info("SAVING YOUR DABASE...")
        vector_store.save_local(FAISS_INDEX_PATH)
        logger.info("Data BASE SAVED...")
        return vector_store
    except Exception as e:
        error_message=CustomException("UNABLE TO SAVE VECTOR STORE!!!",e)
        logger.error(str(error_message))
        raise error_message