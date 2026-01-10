from flask import Flask, redirect, render_template, request, url_for, jsonify
from dotenv import load_dotenv
import os
import git
import hmac
import hashlib
from db import db_read, db_write
from auth import login_manager, authenticate, register_user
from flask_login import login_user, logout_user, login_required, current_user
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Load .env variables
load_dotenv()
W_SECRET = os.getenv("W_SECRET")

# Init flask app
app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = "supersecret"

# Init auth
login_manager.init_app(app)
login_manager.login_view = "login"

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

# Auth routes
@app.get('/users')
@login_required
def users():
    return'Hello from users'
    
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user = authenticate(
            request.form["username"],
            request.form["password"]
        )

        if user:
            login_user(user)
            return redirect(url_for("index"))

        error = "Benutzername oder Passwort ist falsch."

    return render_template(
        "auth.html",
        title="In dein Konto einloggen",
        action=url_for("login"),
        button_label="Einloggen",
        error=error,
        footer_text="Noch kein Konto?",
        footer_link_url=url_for("register"),
        footer_link_label="Registrieren"
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        ok = register_user(username, password)
        if ok:
            return redirect(url_for("login"))

        error = "Benutzername existiert bereits."

    return render_template(
        "auth.html",
        title="Neues Konto erstellen",
        action=url_for("register"),
        button_label="Registrieren",
        error=error,
        footer_text="Du hast bereits ein Konto?",
        footer_link_url=url_for("login"),
        footer_link_label="Einloggen"
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))



# App routes
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # GET
    if request.method == "GET":
        todos = db_read("SELECT id, content, due FROM todos WHERE user_id=%s ORDER BY due", (current_user.id,))
        return render_template("main_page.html", todos=todos)

    # POST
    content = request.form["contents"]
    due = request.form["due_at"]
    db_write("INSERT INTO todos (user_id, content, due) VALUES (%s, %s, %s)", (current_user.id, content, due, ))
    return redirect(url_for("index"))

@app.post("/complete")
@login_required
def complete():
    todo_id = request.form.get("id")
    db_write("DELETE FROM todos WHERE user_id=%s AND id=%s", (current_user.id, todo_id,))
    return redirect(url_for("index"))

@app.route('/like_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def like_recipe(recipe_id):
    existing = db_read("SELECT id FROM liked WHERE user_id = %s AND recipe_id = %s", (current_user.id, recipe_id))
    if existing:
        db_write("DELETE FROM liked WHERE user_id = %s AND recipe_id = %s", (current_user.id, recipe_id))
        liked = False
    else:
        db_write("INSERT INTO liked (user_id, recipe_id) VALUES (%s, %s)", (current_user.id, recipe_id))
        liked = True
    like_count_result = db_read("SELECT COUNT(*) as count FROM liked WHERE recipe_id = %s", (recipe_id,))
    like_count = like_count_result[0]['count']
    return jsonify({'liked': liked, 'like_count': like_count})

@app.route('/recipes')
def recipes():
    recipes_data = db_read("SELECT recipe_id, recipe_name, recipe_photo, recipe_instruction, recipe_mengenangaben, recipes_ingredient FROM recipes")
    recipes = []
    for r in recipes_data:
        recipe = dict(r)
        # Lade ingredients
        group = r['recipes_ingredient']
        if group == 1:
            ids = list(range(1,10))
        elif group == 2:
            ids = list(range(10,18))
        elif group == 3:
            ids = list(range(18,23))
        elif group == 4:
            ids = list(range(23,32))
        elif group == 5:
            ids = list(range(32,40))
        else:
            ids = []
        placeholders = ','.join('?' * len(ids))
        ingredients = db_read(f"SELECT ingredient_name FROM ingredient WHERE id IN ({placeholders})", ids)
        recipe['ingredients'] = [i['ingredient_name'] for i in ingredients]
        # Lade like_count
        like_count_result = db_read("SELECT COUNT(*) as count FROM liked WHERE recipe_id = %s", (r['recipe_id'],))
        recipe['like_count'] = like_count_result[0]['count']
        # user_liked
        user_liked_result = db_read("SELECT 1 FROM liked WHERE user_id = %s AND recipe_id = %s", (current_user.id, r['recipe_id']))
        recipe['user_liked'] = len(user_liked_result) > 0
        recipes.append(recipe)
    return render_template('recipes.html', recipes=recipes, current_user=current_user)

if __name__ == "__main__":
    app.run()

