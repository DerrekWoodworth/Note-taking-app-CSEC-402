from flask import Flask, render_template, redirect, request
from markdown2 import Markdown
import pickle
import signal

#notes = pickle.load( open( "save.p", "rb" ) )
notes = [{'id': 0, 'title': 'Shopping list', 'content': 'eggs milk bread'}, {'id': 1, 'title': 'Work Notes', 'content': 'Need to write automation pipeline for kubernetes'}]

app = Flask("Note Taking App")
markdown_instance = Markdown()

def convertToMarkdown(note):
  note2 = {}
  note2['id'] = note['id']
  note2['title'] = note['title']
  note2['content'] = markdown_instance.convert(note['content'])
  return note2


@app.route("/")
def home():
  global notes
  shortenedNotes = list(map(lambda x: {**x.copy(), 'content': x['content'].split('\n')[0]}, notes))
  print("short-notes------------------", shortenedNotes)
  
  return render_template("home.html", notes=list(map(convertToMarkdown, shortenedNotes)))

@app.route("/create")
def create():
  return render_template("edit.html", mode="create")

@app.route('/view/<noteid>')
def view(noteid):
  noteid = int(noteid)
  global notes
  note = list(filter(lambda x: x['id'] == noteid, notes))[0]
  return render_template('view.html', note=convertToMarkdown(note))

@app.route('/edit/<noteid>', methods=['GET', 'POST'])
def edit(noteid):
  noteid = int(noteid)
  global notes
  if request.method == "GET":
    note = list(filter(lambda x: x['id'] == noteid, notes))[0]
    return render_template('edit.html', note=note, mode="edit", num=noteid)
  elif request.method == 'POST':
    editedNote = request.form.copy()
    editedNote['id'] = int(noteid)
    otherNotes = list(filter(lambda x: x['id'] != noteid, notes))
    notes = otherNotes + [editedNote]    
    notes.sort(key=lambda x: x['id'])
    return redirect('/')
  
@app.route('/addNote', methods=['POST'])
def addNote():
  print("HERE")
  global notes
  newNote = request.form.copy()
  newNote['id'] = getNewId()
  print('New note', newNote)
  notes.append(newNote)
  return redirect('/')

@app.route('/delete/<noteid>')
def delete(noteid):
  noteid = int(noteid)
  global notes
  notes = list(filter(lambda x: x['id'] != noteid, notes))
  return redirect('/')

def getNewId():
  global notes
  ids = list(map(lambda x: int(x['id']), notes))
  maxId = max(ids)
  return maxId + 1

def saveNotes(signum, frame):
  global notes
  pickle.dump(notes, open( "save.p", "wb"))
  exit()

if __name__ == "__main__":
  signal.signal(signal.SIGTERM, saveNotes)
  app.run(host="0.0.0.0", port="8080") 
