from utils import *


def parent_name(id_):
    return Folder.query.get(id_).name
extensions=['png',"jpg","jpeg"]

@app.route('/',methods=['GET', 'POST'])
def index():
    result={}
    folders = Folder.query.all()
    for folder in folders:
        result[folder.name]=[{"name":file.name,"id":file.id} for file in File.query.filter_by(folder_id=folder.id).all()]
    
    if request.method == 'POST':
        search_query = request.form.get('search_query', '')
        file_ids = request.form.get('file_ids', '').split(",")
        if file_ids[0]!="":
            try:
                files=[File.query.get(id_) for id_ in file_ids]
                paths=[file.path for file in files]
                pdfs=[path for path in paths if path.endswith(".pdf")]
                images=[path for path in paths if path.split(".")[-1].lower() in extensions]
                merge_pdfs(pdfs,images,"temp/output.pdf")
                return render_template("success.html")
        
            except:
                return render_template("index.html",result=result,error="Erreur")
        else:
            filtered_result = {}
            for folder, files in result.items():
                if search_query.lower() in folder.lower():
                    filtered_result[folder] = files
                else:
                    filtered_files = [file for file in files if search_query.lower() in file['name'].lower()]
                    if filtered_files:
                        filtered_result[folder] = filtered_files

    elif request.method == 'GET':filtered_result=result

    return render_template("index.html",result=filtered_result)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()  
        traverse_folder("testfolder",None)
    app.run(debug=True)
