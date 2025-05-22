from sqlalchemy.orm import Session
from core.db import SessionLocal
from models.db_models import ProcessedText


def main():
    db: Session = SessionLocal()
    texts = db.query(ProcessedText).all()
    print("Records from processed_texts:")
    for t in texts:
        print(f"🟢 ID: {t.id} | User: {t.user_id} | Text: {t.original_text}")
    db.close()


if __name__ == "__main__":
    main()
