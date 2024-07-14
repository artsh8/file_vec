from flask import Flask, request, redirect, url_for, render_template, send_file, flash
from werkzeug.utils import secure_filename
import os
import io
import sqlite3 as sq
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE" # обход ошибки: Error #15: Initializing libomp140.x86_64.dll, but found libiomp5md.dll already initialized
from txtai import Embeddings

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads/"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB
# os.environ["FLSK_SECRET_KEY"] = "sd?fadf43#5q4ghb!x"
app.config["SECRET_KEY"] = os.getenv("FLSK_SECRET_KEY")
ALLOWED_EXTENSIONS = {"txt"}

def txt_to_str(file_name: str) -> str:
  with open(file_name, encoding="utf8") as f:
    data = f.read().replace("\n", "")
  return data

def index_file(embedding: str, file_name: str, file_data: str) -> None:
  embeddings = Embeddings()
  embeddings.load(embedding)
  doc = (file_name, file_data)
  embeddings.upsert((doc,))
  embeddings.save(embedding)

def save_file(file_name: str, file_data: str) -> None:
  with sq.connect("data/file_names.db") as con:
    cur = con.cursor()
    cur.execute("INSERT INTO file_name (id, data) VALUES (?, ?) ON CONFLICT (id) DO UPDATE SET data = excluded.data", (file_name, file_data))
    con.commit()

@app.route("/")
def main_page():
  uploaded_files_count = len(os.listdir(app.config["UPLOAD_FOLDER"]))
  with sq.connect("data/file_names.db") as con:
    cur = con.cursor()
    res = cur.execute("SELECT COUNT(*) FROM file_name")
    res = res.fetchone()[0]
  return render_template("index.html", not_indexed_files_count=uploaded_files_count, indexed_files_count=res)

def is_allowed_ext(filename: str) -> bool:
  return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload():
  files = request.files.getlist("files")
  if not files[0].filename:
    flash("Выберите файлы для загрузки", category="error")
    return redirect(url_for("main_page"))
  for file in files:
    if file and is_allowed_ext(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
      flash(f"Файл {filename} загружен успешно", category="success")
    else:
      flash("Доступна загрузка только .txt файлов", category="error")
  return redirect(url_for("main_page"))

@app.route("/download/<filename>")
def download(filename):
  with sq.connect("data/file_names.db") as con:
    cur = con.cursor()
    res = cur.execute("SELECT data FROM file_name WHERE id = ?", (filename,))
    res = res.fetchone()[0]
  file_data_bytes = res.encode()
  return send_file(
    io.BytesIO(file_data_bytes),
    download_name=filename,
    as_attachment=True
  )

@app.route("/index_files", methods=["POST"])
def index_files():
  all_files = os.listdir(app.config["UPLOAD_FOLDER"])
  files = (f for f in all_files if os.path.isfile(os.path.join(app.config["UPLOAD_FOLDER"], f)))
  for file in files:
    file_data = txt_to_str(app.config["UPLOAD_FOLDER"] + file)
    index_file("npa", file, file_data)
    save_file(file, file_data)
    os.remove(os.path.join(app.config["UPLOAD_FOLDER"], file))
  return redirect(url_for("main_page"))

def search_embedding(embedding: str, keyword: str) -> list[tuple[str, float]]:
  embeddings = Embeddings()
  embeddings.load(embedding)
  return embeddings.search(keyword, 3)

def name_search(name: str) -> list[tuple[str, float]]:
  name = name + "%"
  with sq.connect("data/file_names.db") as con:
    cur = con.cursor()
    res = cur.execute("SELECT id, 0 FROM file_name WHERE id LIKE ?", (name,))
    ids = res.fetchmany(3)
  return ids

@app.route("/search", methods=["GET", "POST"])
def search():
  if request.method == "POST":
    keyword = request.form["keyword"]
    name = request.form["name"]
    if keyword or name:
      context_ids = search_embedding("npa", keyword) if keyword else []
      name_ids = name_search(name) if name else ()
      context_ids_set = set(i[0] for i in context_ids)
      context_ids.extend(item for item in name_ids if item[0] not in context_ids_set)
      ids = context_ids
      print("Результаты поиска с точностью совпадения:", ids)
    else:
      ids = ()
    return render_template("search.html", ids=ids)
  return render_template("search.html", ids=())

if __name__ == "__main__":
  app.run(debug=True)
  