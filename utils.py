from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
db = SQLAlchemy(app)

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'))
    parent = db.relationship('Folder', remote_side=[id], backref='children')

    def __repr__(self):
        return f"Folder('{self.name}')"

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    path=db.Column(db.String(255))
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))

    def __repr__(self):
        return f"File('{self.name}')"
    
def traverse_folder(folder,parent):
    current_folder=Folder(name=folder,parent=parent)
    db.session.add(current_folder)
    db.session.commit()
    folder_id=current_folder.id
    for record in os.listdir(folder):
        if os.path.isfile(f"{folder}/{record}"):
            current_file=File(name=record,folder_id=folder_id,path=f"{folder}/{record}")
            db.session.add(current_file)
            db.session.commit()
        if os.path.isdir(f"{folder}/{record}"):
            traverse_folder(f"{folder}/{record}",current_folder)
            
        


def merge_pdfs(pdf_list, image_list, output_filename):
    merger = PyPDF2.PdfMerger()
    
    for pdf in pdf_list:
        merger.append(pdf)
    
    for img_path in image_list:

        img = Image.open(img_path)
        pdf_path = img_path.replace('.jpg', '.pdf') 
        img.save(pdf_path, 'PDF')
        merger.append(pdf_path)
    
    with open(output_filename, 'wb') as output_file:
        merger.write(output_file)
