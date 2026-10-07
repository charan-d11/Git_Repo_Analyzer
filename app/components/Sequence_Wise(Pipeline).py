from app.components.load_git_repo import load_git_repo,create_repo_chunks
from app.components.vector import save_vector
from app.common.logger import get_logger

logger=get_logger(__name__)

def pipeline(repo_url:str):
    docs=load_git_repo(repo_url)
    chunks=create_repo_chunks(docs)
    index=save_vector(chunks)
    return index

if __name__ == "__main__":
    pipeline()