from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_secret'

# --- Helper functions ---
def get_todos():
    with open('todos.json', 'r') as f:
        return json.load(f)

def save_todos(todos):
    with open('todos.json', 'w') as f:
        json.dump(todos, f, indent=4)

@app.route('/')
def index():
    todos = get_todos()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add():
    todos = get_todos()

    if len(todos) >= 8:
        flash("Cannot add more than 8 tasks!")
        return redirect(url_for('index'))

    task_text = request.form['task']

    if task_text.strip() == "":
        flash("Task cannot be empty!")
        return redirect(url_for('index'))

    # generate unique id
    new_id = 1 if not todos else max(todo["id"] for todo in todos) + 1

    new_task = {
        "id": new_id,
        "task": task_text,
        "status": "Pending"
    }

    todos.append(new_task)
    save_todos(todos)

    flash("Task added successfully!")
    return redirect(url_for('index'))

@app.route('/update/<int:task_id>')
def update_task(task_id):
    todos = get_todos()
    for todo in todos:
        if todo["id"] == task_id:
            todo["status"] = "Done"
            break
    save_todos(todos)
    flash("Task marked as done!")
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    todos = get_todos()
    todos = [todo for todo in todos if todo["id"] != task_id]

    # Reassign IDs after deletion
    for i, todo in enumerate(todos):
        todo["id"] = i + 1

    save_todos(todos)
    flash("Task deleted successfully!")
    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    todos = get_todos()
    todo = next((t for t in todos if t['id'] == task_id), None)
    if not todo:
        flash("Task not found!")
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_text = request.form['task'].strip()
        if new_text == "":
            flash("Task cannot be empty!")
        else:
            todo['task'] = new_text
            save_todos(todos)
            flash("Task updated successfully!")
            return redirect(url_for('index'))

    return render_template('edit.html', todo=todo)

@app.route('/exit')
def exit_app():
    save_todos([])  # clear all tasks
    flash("All tasks cleared!")
    return redirect(url_for('index'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway sets PORT automatically
    app.run(host="0.0.0.0", port=port)
