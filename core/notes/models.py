from core.models import db
from datetime import datetime
from core.accounts.models import Admin1


class Notes(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author = db.relationship("Admin1", secondary="notes_author", lazy=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(
        db.Text,
    )
    file = db.Column(db.String(60))
    tags = db.relationship("Tags", secondary="notes_tags", lazy=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    lastly_modified = db.Column(
        db.DateTime, onupdate=datetime.utcnow, default=datetime.utcnow
    )


class Tags(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    highlight = db.Column(
        db.Text,
    )
    theme = db.Column(
        db.String(30),
        default="pale-green",
    )
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Tag %r>" % self.id

    def __str__(self):
        return self.name


class NotesAuthor(db.Model):
    """Links notes with author"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    notes_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "notes.id",
        ),
    )
    admins_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "admins.id",
        ),
    )


class NotesTags(db.Model):
    """Links notes with tags"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    notes_id = db.Column(db.Integer, db.ForeignKey("notes.id"))
    tags_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "tags.id",
        ),
    )
