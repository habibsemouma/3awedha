from flask import Flask, render_template,g, request,jsonify
import os
import sqlite3
import win32print
import pathlib
import printfactory
import PyPDF2

printer = printfactory.Printer()
print_tool = printfactory.AdobeReader(printer,app_path=pathlib.Path(r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"))


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
    cur.execute('create table if not exists files( id integer primary key,name text,category text,specificity text,file_path text) ')
    for category in os.listdir(root_dir):
        for specificity in os.listdir(f"{root_dir}/{category}"):
            if os.path.isfile(f"{root_dir}/{category}/{specificity}"):
                file_path=f"{root_dir}/{category}/{specificity}"
                cur.execute(f"insert into files(name,category,file_path) values(?,?,?)",(specificity, category,file_path))
            else:
                for final in os.listdir(f"{root_dir}/{category}/{specificity}"):
                     file_path=f"{root_dir}/{category}/{specificity}/{final}"
                     cur.execute(f"insert into files(name,category,specificity,file_path) values(?,?,?,?)",(final, category, specificity,file_path))
    
    cur.close()
    cur=db.cursor()
    cur.execute("SELECT category,GROUP_CONCAT(id, ', '), GROUP_CONCAT(name, ', '), GROUP_CONCAT(file_path, ', ') FROM files GROUP BY category")
    rows=cur.fetchall()
    return rows


def merge_pdfs(file_paths, output_path):
    merger = PyPDF2.PdfMerger()
    for file_path in file_paths:
        merger.append(file_path)
    merger.write(output_path)
    merger.close()
    return(output_path)


@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        file_paths = request.form.getlist('files')
        final=merge_pdfs([x.replace(" ","",1) for x in file_paths],"temp/output.pdf")
        print_tool.print_file(pathlib.Path(final))
        return jsonify({"success":True})

    else:
        result={}
        rows=get_files_by_folder('testfolder')
        for row in rows:
            category=row[0]
            result[category]=[]
            for (identifier,name,file_path) in zip(row[1].split(","),row[2].split(","),row[3].split(",")):
                result[category].append([identifier,name,file_path])
        return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
