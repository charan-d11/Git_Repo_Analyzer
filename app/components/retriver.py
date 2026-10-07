from langchain.chains import RetrievalQA
from app.common.logger import get_logger
from app.common.coustume_exception import CustomException
from app.components.llm import load_llm
from langchain.prompts import PromptTemplate
from app.components.vector import load_vector

logger=get_logger(__name__)

CUSTOM_PROMPT = """
You are an expert GitHub Repository Assistant. 
Your job is to help developers understand unfamiliar codebases by answering questions based ONLY on the repository context provided.

Use the following context from the repository to answer the question at the end.

Context:
{context}

Question:
{question}

Guidelines:
- Answer ONLY based on the context provided above.
- If the answer is not in the context, say "I could not find this in the repository. Please make sure the repository is indexed correctly."
- When explaining code, mention the file name and what it does.
- Keep answers clear, structured and developer-friendly.
- If asked about a function or class, explain what it does, its parameters and return values.
- If asked where something is implemented, mention the exact file path from metadata.

Helpful Answer:
"""


def set_costom_prompt():
    return PromptTemplate(
        template=CUSTOM_PROMPT,
        input_variables=["context", "question"]
    )

def create_qa_chain():
    try:
        logger.info("Loading Vectorstore for your context")
        vector=load_vector()
        if vector is None:
            raise CustomException('Vectorstore Not Present')
        llm=load_llm()
        if llm is None:
            raise CustomException('LLM is not loaded.')

        qa_chain=RetrievalQA.from_chain_type(
            llm=llm,
            chain_type='stuff',     
            retriever=vector.as_retriever(search_kwargs={'k':3}),
            chain_type_kwargs={'prompt':set_costom_prompt()}
        )
        logger.info("Successfully created the QA chain")
        return qa_chain
    except Exception as e:
        error_message=CustomException("faild To Create QA Chain",e)
        logger.error(str(error_message))
        return None