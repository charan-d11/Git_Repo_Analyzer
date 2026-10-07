from flask import Flask, render_template, request, session, jsonify
from app.components.retriver import create_qa_chain
from app.components.load_git_repo import load_git_repo, create_repo_chunks
from app.components.vector import save_vector
from dotenv import load_dotenv
from markupsafe import Markup
import os
import threading


load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
indexing_status = {
    "state": "idle",      
    "repo_name": "",
    "message": ""
}

def br_tag(value):
    return Markup(value.replace("\n", "<br>\n"))
app.jinja_env.filters['br_tag'] = br_tag

def run_pipeline(repo_url: str):
    global indexing_status
    try:
        indexing_status["state"] = "indexing"
        indexing_status["message"] = "Cloning repository..."

        docs = load_git_repo(repo_url)
        if not docs:
            raise Exception("No supported files found in repo.")

        indexing_status["message"] = "Creating chunks..."
        chunks = create_repo_chunks(docs)
        if not chunks:
            raise Exception("Failed to create chunks.")

        indexing_status["message"] = "Building FAISS index..."
        save_vector(chunks)

        repo_name = repo_url.rstrip('/').split('/')[-1].replace(".git", "")
        indexing_status["state"]     = "done"
        indexing_status["repo_name"] = repo_name
        indexing_status["message"]   = f"✅ {repo_name} indexed successfully!"

        app.config["QA_CHAIN"] = create_qa_chain()

    except Exception as e:
        indexing_status["state"]   = "error"
        indexing_status["message"] = f"Error: {str(e)}"

@app.route('/index-repo', methods=['POST'])
def index_repo():
    global indexing_status

    if indexing_status["state"] == "indexing":
        return jsonify({"status": "indexing", "message": "Already indexing a repo, please wait..."})

    data = request.get_json()
    repo_url = data.get("repo_url", "").strip()

    if not repo_url:
        return jsonify({"status": "error", "message": "No URL provided."})

    if "github.com" not in repo_url:
        return jsonify({"status": "error", "message": "Please provide a valid GitHub URL."})

    indexing_status = {"state": "idle", "repo_name": "", "message": ""}
    session.pop("messages", None)

    thread = threading.Thread(target=run_pipeline, args=(repo_url,))
    thread.daemon = True
    thread.start()

    return jsonify({"status": "started", "message": "Indexing started..."})

@app.route('/status', methods=['GET'])
def status():
    return jsonify(indexing_status)

@app.route('/', methods=['GET', 'POST'])
def index():
    session.setdefault("messages", [])

    if request.method == "POST":
        user_input = request.form.get("prompt")

        if user_input:
            try:
                qa_chain = app.config.get("QA_CHAIN")
                if qa_chain is None:
                    raise Exception("Please index a repository first.")

                response = qa_chain.invoke({"query": user_input})
                result = response.get("result", "No result found.")

                session["messages"].append({
                    "user": user_input,
                    "bot": result
                })
                session.modified = True

            except Exception as e:
                session["messages"].append({
                    "user": user_input,
                    "bot": f"Error: {str(e)}"
                })
                session.modified = True

    return render_template(
        "index.html",
        messages=session["messages"],
        indexing_status=indexing_status
    )


#clear chat 
@app.route('/clear', methods=['POST'])
def clear():
    session.pop("messages", None)
    return render_template(
        "index.html",
        messages=[],
        indexing_status=indexing_status
    )


if __name__ == "__main__":
    app.config["QA_CHAIN"] = None
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )