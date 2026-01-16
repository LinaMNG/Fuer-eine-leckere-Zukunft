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
    return 'Hello from users'
    
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
    return redirect('/recipes', code=303)

@app.route('/recipes')
def recipes():
    try:
        # Fetch recipes with their like counts
        recipes = db_read("""
            SELECT 
                r.recipe_id,
                r.recipe_name,
                r.recipe_photo,
                r.recipe_instruction,
                r.recipe_mengenangaben,
                COALESCE(l.like_count, 0) as like_count
            FROM recipes r
            LEFT JOIN (
                SELECT recipe_id, COUNT(*) as like_count 
                FROM liked 
                GROUP BY recipe_id
            ) l ON r.recipe_id = l.recipe_id
            ORDER BY r.recipe_id
        """)
        
        # Add user_liked status for each recipe if user is authenticated
        if current_user.is_authenticated:
            # Get all recipe IDs that the current user has liked
            liked_recipe_ids = db_read(
                "SELECT recipe_id FROM liked WHERE user_id = %s",
                (current_user.id,)
            )
            # Convert to a set for fast lookup
            liked_set = {item['recipe_id'] for item in liked_recipe_ids}
            
            # Add user_liked flag to each recipe
            for recipe in recipes:
                recipe['user_liked'] = recipe['recipe_id'] in liked_set
        else:
            for recipe in recipes:
                recipe['user_liked'] = False
        
        return render_template(
            'recipes.html', 
            recipes=recipes,
            current_user=current_user
        )
    except Exception as e:
        print(f"FEHLER in /recipes route: {e}")
        import traceback
        traceback.print_exc()
        return render_template('recipes.html', recipes=[], current_user=current_user, error="Fehler beim Laden der Rezepte")

@app.route('/liked_recipes')
@login_required
def liked_recipes():
    try:
        # Fetch recipes that the current user has liked
        recipes = db_read("""
            SELECT 
                r.recipe_id,
                r.recipe_name,
                r.recipe_photo,
                r.recipe_instruction,
                r.recipe_mengenangaben,
                COALESCE(l.like_count, 0) as like_count
            FROM recipes r
            INNER JOIN liked ul ON r.recipe_id = ul.recipe_id
            LEFT JOIN (
                SELECT recipe_id, COUNT(*) as like_count 
                FROM liked 
                GROUP BY recipe_id
            ) l ON r.recipe_id = l.recipe_id
            WHERE ul.user_id = %s
            ORDER BY r.recipe_id
        """, (current_user.id,))
        
        # Add user_liked status for each recipe (they're all liked since we fetched only liked ones)
        for recipe in recipes:
            recipe['user_liked'] = True
        
        return render_template(
            'likedrecipes.html', 
            recipes=recipes,
            current_user=current_user
        )
    except Exception as e:
        print(f"FEHLER in /liked_recipes route: {e}")
        import traceback
        traceback.print_exc()
        return render_template('likedrecipes.html', recipes=[], current_user=current_user, error="Fehler beim Laden der Lieblingsrezepte")
        
@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipe = db_read("SELECT * FROM recipes WHERE recipe_id=%s", (recipe_id,), single=True)
    if recipe:
        # Zutaten über die contains-Tabelle laden (nur ingredient_name)
       ingredients = db_read(
    """
    SELECT 
        i.ingredient_name,
        c.menge
    FROM contains c
    JOIN ingredient i ON c.ingredient_id = i.id
    WHERE c.recipe_id = %s
    ORDER BY i.ingredient_name
    """,
    (recipe_id,)
)

        # db_read liefert Liste von dicts mit key 'ingredient_name'
        recipe['ingredients'] = ingredients
        return render_template('receipe_detail.html', recipe=recipe)
    return render_template('receipe_detail.html', recipe=None, error="Rezept nicht gefunden"), 404


@app.route('/search')
def search_recipes():
    ingredient = request.args.get('ingredient', '').strip()
    diets = request.args.getlist('diet')  # checkboxen

    if not ingredient:
        return redirect(url_for('recipes'))

    # Dynamische Bedingungen für HAVING
    having_conditions = []
    if 'vegetarisch' in diets:
        having_conditions.append("SUM(CASE WHEN i2.vegetarisch = FALSE THEN 1 ELSE 0 END) = 0")
    if 'vegan' in diets:
        having_conditions.append("SUM(CASE WHEN i2.vegan = FALSE THEN 1 ELSE 0 END) = 0")
    if 'laktosefrei' in diets:
        having_conditions.append("SUM(CASE WHEN i2.laktose = FALSE THEN 1 ELSE 0 END) = 0")
    if 'glutenfrei' in diets:
        having_conditions.append("SUM(CASE WHEN i2.ingredient_glutenfrei = FALSE THEN 1 ELSE 0 END) = 0")

    having_sql = ""
    if having_conditions:
        having_sql = " AND " + " AND ".join(having_conditions)

    # SQL: nur Rezepte, die die gesuchte Zutat enthalten und keine Zutat die Bedingungen verletzt
    query = f"""
        SELECT 
            r.recipe_id,
            r.recipe_name,
            r.recipe_photo,
            r.recipe_instruction,
            r.recipe_mengenangaben,
            COALESCE(l.like_count, 0) AS like_count
        FROM recipes r
        LEFT JOIN (
            SELECT recipe_id, COUNT(*) AS like_count
            FROM liked
            GROUP BY recipe_id
        ) l ON r.recipe_id = l.recipe_id
        WHERE r.recipe_id IN (
            SELECT c2.recipe_id
            FROM contains c2
            JOIN ingredient i2 ON c2.ingredient_id = i2.id
            GROUP BY c2.recipe_id
            HAVING
                SUM(CASE WHEN LOWER(i2.ingredient_name) = LOWER(%s) THEN 1 ELSE 0 END) > 0
                {having_sql}
        )
        ORDER BY r.recipe_id
    """

    recipes = db_read(query, (ingredient,))

    # user_liked setzen
    if current_user.is_authenticated:
        liked_ids = db_read(
            "SELECT recipe_id FROM liked WHERE user_id = %s",
            (current_user.id,)
        )
        liked_set = {x["recipe_id"] for x in liked_ids}
        for r in recipes:
            r["user_liked"] = r["recipe_id"] in liked_set
    else:
        for r in recipes:
            r["user_liked"] = False

    return render_template(
        "recipes.html",
        recipes=recipes,
        current_user=current_user,
        search_ingredient=ingredient
    )


if __name__ == "__main__":
    app.run()

