import os
from dotenv import load_dotenv

load_dotenv()

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# print(BASE_DIR)

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join('db.sqlite3')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False

    # Worker settings
    INTERVAL_SEC = int(os.getenv("INTERVAL_SEC", "300"))

    # Ponisha API
    
    PONISHA_BEARER = os.getenv("token")
    PONISHA_USER_ID = os.getenv("user_id")
    PONISHA_API="https://search.ponisha.ir/v1/projects/search"
    PONISHA_PER_PAGE=20
    PONISHA_SORT="billboarded_at"
    PONISHA_ORDER="desc"
    INTERVAL_SEC=300
    HOST="0.0.0.0"
    PORT="8000"
    DEBUG=0
