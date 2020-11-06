from flask import Flask, render_template, request, session, redirect
import json
import re
import uuid

app = Flask(__name__)
# In a production environment, this shouldn't be here!
app.secret_key = "5c8fce510fa3c5f9bb251cd1b13fd6eb"

todo_list = []

def load_saved_todo_list():
    global todo_list
    try:
        with open('todo_list.json') as f: todo_list = json.load(f)
    except (OSError, IOError):
        with open('todo_list.json', 'w') as f: json.dump(todo_list, f)

load_saved_todo_list()

# Index route
@app.route('/')
def index():
    return render_template("todoapp.html",
                           todo_list=todo_list,
                           errors=session.pop("errors", None),
                           alert=session.pop("alert", None)
                           )

@app.route("/submit", methods=["POST"])
def submit():
    def validate():
        validation_errors = {"messages": {}, "input": {}}

        if (request.form["task"].strip() == ""):
            validation_errors["messages"].update(
                {"task": "Task required."})

        if not re.search(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', request.form["email"]):
            validation_errors["messages"].update( {"email": "A valid email address is required."})

        if request.form["priority"] not in ["Low", "Medium", "High"]:
            validation_errors["messages"].update( {"priority": "Please select a todo priority."})

        if validation_errors["messages"]: validation_errors.update({"input": dict(request.form)})
        else: validation_errors = {}

        return validation_errors

    validation = validate()

    if not validation:
        todo_id = str(uuid.uuid4())
        todo_list.append({
            "id": todo_id,
            "task": request.form["task"],
            "email": request.form["email"],
            "priority": request.form["priority"]
        })

        session["alert"] = { "level": "success", "message": "To-Do item added, remember to save the changes!" }

        return redirect("/#todo-"+todo_id)
    else:
        session["errors"] = validation
        return redirect("/#add-todo")

@app.route("/clear", methods=["POST"])
def clear():
    global todo_list
    if len(todo_list) > 0:
        todo_list = []
        session["alert"] = { "level": "info", "message": "To-Do list cleared!" }

    else:
        session["alert"] = { "level": "info", "message": "To-Do list already empty, nothing to clear!" }

    return redirect("/")

@app.route("/save", methods=["POST"])
def save():
    with open('todo_list.json', 'w') as f: json.dump(todo_list, f)

    session["alert"] = { "level": "success", "message": "To-Do list saved!"}

    return redirect("/")

@app.route("/delete/<todo_id>")
def delete(todo_id):
    global todo_list

    todo_list = list(filter(lambda todo, todo_id=todo_id: todo["id"] != todo_id, todo_list))

    session["alert"] = {"level": "info","message": "To-Do task deleted!"}

    return redirect("/")


if __name__ == '__main__':
    app.run()
