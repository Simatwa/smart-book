from core.models import db
from datetime import datetime
from core.accounts.models import Admin1
import markdown, re, logging
from flask import url_for
from os import path
from core.app import markdown_extensions


class Notes(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author = db.relationship("Admin1", secondary="notes_author", lazy=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(
        db.Text,
    )
    intro = db.Column(db.Text, nullable=True, default="")
    file = db.Column(db.String(60))
    tags = db.relationship("Tags", secondary="notes_tags", lazy=True)
    views = db.Column(db.Integer, default=0)
    is_markdown = db.Column(db.Boolean, default=False)
    is_pinned = db.Column(db.Boolean, default=False)
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
        default="blue",
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


class LocalEventListener:
    @staticmethod
    def delete_file(mapper, connections, target):
        if target.file:
            abs_path = path.join(FILES_DIR, target.file)
            try:
                remove(abs_path)
            except Execption as e:
                logging.error("Failed to delete file - '%s' - %s" % (abs_path, e))

    @staticmethod
    def generate_html_tag(filename: str):
        extension = path.splitext(filename)[1].lower()
        # image_extensions = [".jpg", ".jpeg", ".png", ".gif"]
        video_extensions = [
            ".mp4",
            ".avi",
            ".mov",
            ".mkv",
            ".3gp",
            ".webm",
        ]
        audio_extensions = [".mp3", ".wav", ".flac", ".ogg"]
        # if extension in image_extensions:
        # resp = f'<img class="w3-image" src="{filename}" alt="Image">'
        if extension in video_extensions:
            resp = f"""
	   	<div class="w3-center w3-padding">	   	
	   	    <video  controls>
	   	   <source src="{filename}" type="video/{extension[1:]}">
	   	</video>
	   	</div>"""
        elif extension in audio_extensions:
            resp = f"""
	   	<div class="w3-center w3-padding">
	   	  <audio controls>
	   	  <source src="{filename}" type="audio/{extension[1:]}">
	   	</audio>
	   	</div>"""
        else:
            # resp = filename
            resp = f"""
            <div class="w3-center w3-padding">
            <div class="w3-block w3-light-blue w3-border-large" style="margin-left:20%;margin-right:20%;">
             <p>
              <a href="{filename}" class="w3-xxlarge">
              <i class="fa fa-download w3-xxlarge"></i>({extension})
              </a>
             </p>
            </div>
            </div>
            """
        return resp.strip()

    @staticmethod
    def add_w3_styles(target):
        """Adds w3-styles to htmls"""
        tags_dict = {
            "<img": '<IMG class="w3-image w3-center w3-padding w3-hover-opacity"',
            "<table": '<TABLE class="w3-table-all w3-center w3-hoverable w3-responsive"',
            # "<thead" : '<THEAD class="w3-orange"',
            "<code>": '<CODE class="w3-codespan">',
            "<a ": '<A class="link" ',
        }
        for tag in tags_dict:
            target.content = re.sub(tag, tags_dict[tag], target.content)

    @staticmethod
    def format_markdown_article(mapper, connections, target):
        if target.is_markdown and target.content:
            target.content = (
                target.content.replace("%(", "(}}}}")
                .replace("%", "%%")
                .replace("(}}}}", "%(")
            )
            gen_file_link = lambda name: url_for(
                "static", filename="files/" + str(name)
            )
            kwargs = {}
            if target.file:
                kwargs["file"] = LocalEventListener.generate_html_tag(
                    gen_file_link(target.file)
                )

            target.content = markdown.markdown(
                target.content % kwargs, extensions=markdown_extensions
            )
            LocalEventListener.add_w3_styles(target)


db.event.listen(Notes, "before_insert", LocalEventListener.format_markdown_article)
db.event.listen(Notes, "before_update", LocalEventListener.format_markdown_article)
db.event.listen(Notes, "before_delete", LocalEventListener.delete_file)
