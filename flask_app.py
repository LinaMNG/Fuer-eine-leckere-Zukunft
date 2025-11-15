from flask import Flask, redirect, render_template, request, url_for
from dotenv import load_dotenv
import os
import git
import hmac
import hashlib
from db import db_execute

# Load .env variables
load_dotenv()
W_SECRET = os.getenv("W_SECRET")

# Init flask app
app = Flask(__name__)
app.config["DEBUG"] = True


# DON'T CHANGE
def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)

# DON'T CHANGE
@app.post('/update_server')
def webhook():
    x_hub_signature = request.headers.get('X-Hub-Signature')
    if is_valid_signature(x_hub_signature, request.data, W_SECRET):
        repo = git.Repo('./mysite')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    return 'Unathorized', 401

@app.route("/", methods=["GET", "POST"])
def index():
    # GET
    if request.method == "GET":
        todos = db_execute("SELECT id, content, due FROM todos ORDER BY due")
        return render_template("main_page.html", todos=todos)

    # POST
    content = request.form["contents"]
    due = request.form["due_at"]
    db_execute("INSERT INTO todos (content, due) VALUES (%s, %s)", (content, due, ), True)
    return redirect(url_for("index"))

@app.post("/complete")
def complete():
    todo_id = request.form.get("id")
    db_execute("DELETE FROM todos WHERE id=%s", (todo_id,), True)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run()
