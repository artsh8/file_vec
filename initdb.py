import sqlite3 as sq
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE" # обход ошибки: Error #15: Initializing libomp140.x86_64.dll, but found libiomp5md.dll already initialized
from txtai import Embeddings

def create_e(name: str, path: str) -> None:
  embeddings = Embeddings(path=path, content=False, autoid=False)
  doc = ("init.txt", "data")
  embeddings.upsert((doc,))
  embeddings.save(name)
  embeddings.load(name)
  embeddings.delete(["init.txt"])
  embeddings.save(name)

if __name__ == "__main__":
  create_e("npa", "snagbreac/russian-reverse-dictionary-semsearch")
#   create_e("npa1", "siberian-lang-lab/evenki-russian-parallel-corpora") 
#   create_e("npa2", "sergeyzh/rubert-tiny-turbo")
  
  os.mkdir("uploads")
  os.mkdir("data")
  
  with sq.connect('data/file_names.db') as con:
    cur = con.cursor()
    cur.execute("PRAGMA journal_mode=WAL")
    cur.execute("DROP TABLE IF EXISTS file_name")
    cur.execute("CREATE TABLE IF NOT EXISTS file_name (id TEXT PRIMARY KEY NOT NULL, data TEXT)")
    con.commit()
