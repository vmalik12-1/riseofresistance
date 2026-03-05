from typing import Optional
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return db.session.get(Admin, int(id))


class Mutation(db.Model):
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    aa_mut : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(20))
    source : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(500))
    bp_mut : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(20))
    species : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(20))

    def __repr__(self):
        return 'Key id: {} - aa_mut: {} - bp_mut: {} - species {}>'.format(self.id,self.aa_mut,self.bp_mut, self.species)
    
    def get_aa_mut(self):
        return self.aa_mut
    
    def get_bp_mut(self):
        return self.bp_mut
    
    def get_spec(self):
        return self.species
    
    def get_source(self):
        return self.source

class NewMutation(db.Model):
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    aa_mut : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(20))
    source : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(500))
    bp_mut : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(20))
    species : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(20))

    def __repr__(self):
        return 'Key id: {} - aa_mut: {} - bp_mut: {} - species {}>'.format(self.id,self.aa_mut,self.bp_mut, self.species)
    
    def get_aa_mut(self):
        return self.aa_mut
    
    def get_bp_mut(self):
        return self.bp_mut
    
    def get_species(self):
        return self.species
    
    def get_source(self):
        return self.source

    
class Admin(UserMixin, db.Model):
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    username : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), index = True, unique = True)
    password_hash : sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(256))
    
    def __repr__(self):
        return '<Admin ID: {} - username: {}'.format(self.id, self.username)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_username(self):
        return self.username
