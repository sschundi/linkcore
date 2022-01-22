import os
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, timedelta
from helpers import *



# Configure application
app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


app.permanent_session_lifetime = timedelta(days=365)
app.secret_key = os.getenv('SECRET_KEY', 'for dev')


# Default form input
default = "Untitled"
page = "home"


@app.route("/addtodo", methods=["POST"])
#@login_required
def addtodo():
    """Add a to-do list directly from homepage"""

    # Extract and format inputs
    listname = request.form.get("listname_t")
    duedate = request.form.get("duedate_t")
    if not listname:
        listname = default
    if not duedate:
        duedate = None

    # Insert new list into "to-do" table
    add_todo_list(listname, duedate)

    # Redirect user to home page
    return redirect("/")


@app.route("/deletetodo/<int:todoid>")
#@login_required
def deletetodo(todoid):
    """Delete a to-do list"""

    # Update "to-do" table to reflect to-do list as deleted
    delete_todo_list(todoid)

    # Redirect user to home page
    return redirect("/")


@app.route("/ticktodo/<int:todoid>")
#@login_required
def ticktodo(todoid):
    """Complete a to-do list"""

    # Update "to-do" table to reflect to-do list as completed
    tick_todo_list(todoid)

    # Redirect user to home page
    return redirect("/")


@app.route("/edittodo/<int:todoid>", methods=["GET", "POST"])
#@login_required
def edittodo(todoid):
    """Edit a to-do list"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Extract inputs
        listname = request.form.get("listname")
        duedate = request.form.get("duedate")
        if not duedate:
            duedate = None

        # Update to-do list details in "to-do" table
        edit_todo_list(todoid, listname, duedate)

        # todo
        page = "home"

        # Render homepage
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        #Call today's date
        today = date.today()

        # Query to-do list details
        todo_list = query_todo_list_details(todoid)
        listname = todo_list["listname"]
        duedate = todo_list["duedate"]

        # Query and format un-deleted items in to-do list
        items = query_todo_list(todoid)
        format_list(items)

        page = "edit_t"

        # Render edittodo page after an item is updated
        return render_template("edittodo.html", listname=listname, duedate=duedate, items=items, todoid=todoid, today=today, page=page)


@app.route("/addtodoitem/<int:todoid>", methods=["POST"])
#@login_required
def addtodoitem(todoid):
    """Add a to-do list item"""

    # Extract and format inputs
    duedate = request.form.get("duedate_t")
    itemname = request.form.get("itemname")
    if not itemname:
        itemname = default
    if not duedate:
        duedate = None

    # Insert new list into "todoitem" table
    add_todo_item(todoid, itemname, duedate)

    # Render edittodo page after an item is updated
    return redirect(url_for("edittodo", todoid=todoid))


@app.route("/deletetodoitem/<int:itemid>/<int:todoid>")
def deletetodoitem(itemid, todoid):
    """Delete a to-do list item"""

    # Update "todoitem" table to reflect item as deleted
    delete_todo_item(itemid)

    # Render edittodo page after an item is updated
    return redirect(url_for("edittodo", todoid=todoid))


@app.route("/ticktodoitem/<int:itemid>/<int:todoid>")
#@login_required
def ticktodoitem(itemid, todoid):
    """Complete a to-do list item"""

    # Update "todoitem" table to reflect item as completed
    tick_todo_item(itemid)

    # Render edittodo page after an item is updated
    return redirect(url_for("edittodo", todoid=todoid))

@app.route("/del_all_todoitem/<int:todoid>", methods=["POST"])
#@login_required
def del_all_todoitem(todoid):
    """Delete all to-do list items"""

    # Update "todoitem" table to reflect all items as deleted
    delete_todoitems(todoid, True)
    delete_todoitems(todoid, False)

    # Redirect to edittodo page after items are updated
    return redirect(url_for("edittodo", todoid=todoid))


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
