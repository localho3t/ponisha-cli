from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)  # PK داخلی
    source = db.Column(db.String(32), default="ponisha", index=True)
    external_id = db.Column(db.String(32), unique=True, nullable=False, index=True)  # id پونیشا (رشته)

    title = db.Column(db.String(500), nullable=False)
    slug = db.Column(db.String(600), nullable=True)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(200), nullable=True)

    amount_min = db.Column(db.Integer, nullable=True)
    amount_max = db.Column(db.Integer, nullable=True)

    bidding_closed_at = db.Column(db.DateTime, nullable=True, index=True)
    approved_at = db.Column(db.DateTime, nullable=True, index=True)
    billboarded_at = db.Column(db.DateTime, nullable=True)

    promotions_json = db.Column(db.Text, nullable=True)
    skills_json = db.Column(db.Text, nullable=True)

    project_bids_count = db.Column(db.Integer, nullable=True)
    bidders_json = db.Column(db.Text, nullable=True)

    inserted_at = db.Column(db.DateTime, default=datetime.utcnow, server_default=func.now(), index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "external_id": self.external_id,
            "title": self.title,
            "slug": self.slug,
            "description": self.description,
            "priority": self.priority,
            "amount_min": self.amount_min,
            "amount_max": self.amount_max,
            "bidding_closed_at": self.bidding_closed_at.isoformat() if self.bidding_closed_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "billboarded_at": self.billboarded_at.isoformat() if self.billboarded_at else None,
            "project_bids_count": self.project_bids_count,
            "inserted_at": self.inserted_at.isoformat() if self.inserted_at else None,
        }
