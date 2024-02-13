from flask import Flask, render_template,g, request
import os
import sqlite3
import win32print

def print_files(file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            printer_name = win32print.GetDefaultPrinter()
            win32print.ShellExecute(0, "print", file_path, f'/d:"{printer_name}"', ".", 0)
            print(f"File '{file_path}' sent to printer '{printer_name}'.")
        else:
            print(f"File '{file_path}' does not exist.")

app = Flask(__name__)
DATABASE = 'database.sqlite'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_files_by_folder(root_dir):
    db = get_db()
    cur = db.cursor()
    cur.execute("drop table if exists files")
    cur.execute('create table if not exists files( id integer primary key,name text,category text,specificity text) ')
    for category in os.listdir(root_dir):
        for specificity in os.listdir(f"{root_dir}/{category}"):
            if os.path.isfile(f"{root_dir}/{category}/{specificity}"):
                cur.execute(f"insert into files(name,category) values(?,?)",(specificity, category))
            else:
                for final in os.listdir(f"{root_dir}/{category}/{specificity}"):
                     cur.execute(f"insert into files(name,category,specificity) values(?,?,?)",(final, category, specificity))
    
    cur.close()
    cur=db.cursor()
    cur.execute("SELECT category,GROUP_CONCAT(id, ', '), GROUP_CONCAT(name, ', ') FROM files GROUP BY category")
    rows=cur.fetchall()
    return rows



@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        files = request.form.getlist('files')
        print("activated",files)

    else:
        result={}
        rows=get_files_by_folder('testfolder')
        for row in rows:
            category=row[0]
            result[category]=[]
            for (identifier,name) in zip(row[1].split(","),row[2].split(",")):
                result[category].append([identifier,name])
        return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
