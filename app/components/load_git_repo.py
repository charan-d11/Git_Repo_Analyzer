import os
import git
import stat
import shutil
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config.config import (REPO_PATH, SUPPORTED_EXT, CHUNK_S, CHUNK_O)
from app.common.logger import get_logger
from app.common.coustume_exception import CustomException

logger = get_logger(__name__)

def force_remove(path):
    def handle_error(func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    shutil.rmtree(path, onerror=handle_error)

def load_git_repo(repo_url: str) -> list[Document]:
    try:
        repo_name = repo_url.rstrip('/').split('/')[-1].replace(".git", "")
        clone_path = os.path.join(REPO_PATH, repo_name)
    #first delete exist one
        if os.path.exists(REPO_PATH):
            force_remove(REPO_PATH)
            logger.info(f"Cleared all previous repos from {REPO_PATH}")
        os.makedirs(REPO_PATH, exist_ok=True)

        logger.info(f"CLONING FROM {repo_url} TO {clone_path}")
        git.Repo.clone_from(repo_url, clone_path)

        docs = []

        for root, dirs, files in os.walk(clone_path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]  # skip .git

            for file in files:
                ext = os.path.splitext(file)[1].lower()

                if ext not in SUPPORTED_EXT:
                    continue

                file_path = os.path.join(root, file)

                try:
                    with open(file_path, encoding='utf-8', errors="ignore") as f:
                        content = f.read()

                    if not content.strip():
                        continue  # skip empty files

                    relative_path = os.path.relpath(file_path, clone_path)
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": relative_path,
                            "file_type": ext,
                            "repo": repo_name,
                            "repo_url": repo_url,
                            "file_name": file,
                        }
                    )
                    docs.append(doc)

                except Exception as e:
                    error_message = CustomException("UNABLE TO READ FILE", e)
                    logger.warning(f"Skipping file {file_path}: {error_message}")

        if not docs:
            raise CustomException("NO SUPPORTED FILE FOUND IN THIS REPO!")

        logger.info(f"FINDING {len(docs)} files from {repo_name}")
        return docs

    except Exception as e:
        error_message = CustomException("Failed to load GitHub repository.", e)
        logger.error(str(error_message))
        return []


#docs to chunks ──
def create_repo_chunks(docs: list[Document]) -> list[Document]:
    try:
        if not docs:
            logger.warning("NO DOCS FOUND TO BE CONVERT TO CHUNKS!")
            return []

        logger.info(f"The {len(docs)} no of docs are ready to convert to chunks...")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_S,
            chunk_overlap=CHUNK_O,
            separators=["\nclass ", "\ndef ", "\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(docs)

        logger.info(f"Generated {len(chunks)} chunks from {len(docs)} documents")
        return chunks

    except Exception as e:
        error_message = CustomException("Unable To Create Repo Chunks.", e)
        logger.error(str(error_message))
        return []