import os
import sys

# Ensure backend directory is in python module path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Vercel serverless environment configuration:
# Root directory in AWS Lambda is read-only; /tmp is the writable storage location.
is_vercel = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
if is_vercel:
    tmp_uploads = "/tmp/uploads"
    os.makedirs(tmp_uploads, exist_ok=True)
    if not os.environ.get("UPLOAD_DIR"):
        os.environ["UPLOAD_DIR"] = tmp_uploads
    if not os.environ.get("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "sqlite:////tmp/lostfound.db"

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.category import Category
import app.models as _models  # ensure all SQLAlchemy models are registered
from app.main import app as fastapi_app

app = fastapi_app

# Auto-initialize database tables and demo seed data on fresh deployment
try:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        cat_count = db.query(Category).count()
        if cat_count == 0:
            from scripts.seed_demo_data import seed_all
            seed_all()
    except Exception as seed_err:
        print(f"[Vercel Init] Seed notice: {seed_err}")
    finally:
        db.close()
except Exception as init_err:
    print(f"[Vercel Init] DB setup notice: {init_err}")
