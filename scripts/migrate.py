import os
from sqlalchemy import text
from core.database import init_db, get_db_session
from app import create_app

app = create_app()
init_db(app)
db = get_db_session()

print("Applying migrations...")

migrations = sorted(os.listdir("migrations"))
for file in migrations:
    if file.endswith(".sql"):
        with open(os.path.join("migrations", file)) as f:
            db.execute(text(f.read()))
            print(f"Applied {file}")

db.commit()
print("All migrations applied.")
