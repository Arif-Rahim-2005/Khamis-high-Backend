from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import generate_password_hash, check_password_hash


convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)



class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role= db.Column(db.String(120), nullable=False, default="User")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class System(db.Model):
    __tablename__= "systems"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    departments = db.relationship(
            'Department',
            back_populates='system',
            lazy=True,
            cascade="all, delete"
        )   
    subject_selections = db.relationship('SubjectSelection', back_populates='system', cascade='all, delete')

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

    
class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    system_id = db.Column(db.Integer, db.ForeignKey('systems.id'), nullable=False)

    # ✅ Correct way to reference back to System
    system = db.relationship('System', back_populates='departments')
    subject_selections = db.relationship('SubjectSelection', back_populates='department', cascade='all, delete')

    # ✅ Relationship to Track
    tracks = db.relationship('Track', back_populates='department', cascade='all, delete')

    subjects = db.relationship('Subject', back_populates='department', lazy=True)
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)

    subjects = db.relationship('Subject', back_populates='track', lazy=True)
    department = db.relationship('Department', back_populates='tracks')
    subject_selections = db.relationship('SubjectSelection', back_populates='track', cascade='all, delete')


    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), nullable=True)
    system_id = db.Column(db.Integer, db.ForeignKey('systems.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)

    track = db.relationship('Track', back_populates='subjects')
    department = db.relationship('Department', back_populates='subjects')
    system = db.relationship('System', lazy=True)
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"


class ClubandSociety(db.Model):
    __tablename__ = 'clubs_and_societies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    image_path= db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

class SubjectSelection(db.Model):
    __tablename__ = 'subject_selections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subjects = db.Column(db.Text, nullable=False)  # stored as JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    system_id = db.Column(db.Integer, db.ForeignKey('systems.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), nullable=True)

    # Relationships
    system = db.relationship('System', back_populates='subject_selections')
    department = db.relationship('Department', back_populates='subject_selections')
    track = db.relationship('Track', back_populates='subject_selections')

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"


class Alumni(db.Model):
    __tablename__ = 'alumnis'  # lowercase & plural convention
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    current_title = db.Column(db.String(200), nullable=True)
    year_of_completion = db.Column(db.String(10), nullable=True)  # simpler as string (e.g. "2020")
    comment = db.Column(db.String(500), nullable=False)
    image_path = db.Column(db.String(200), nullable=True)  # optional photo

    def __repr__(self):
        return f"<Alumni {self.name}>"





class FeeStructure(db.Model):
    __tablename__= 'fee_structures'
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AboutUsImage(db.Model):
    __tablename__ = 'about_us_images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)