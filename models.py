## Create database models with appropriate parent-child relations

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Define Artists class as the parent class for joining with Venue class

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))
    
    # Realize the many-to-many relation via association proxy
    show = association_proxy("shows", "venues")

    def __repr__(self):
        return f'<Artist id: {self.id}, Artist name: {self.name}>'

  # Define Venue class

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String(500))

    # Realize the many-to-many relation via association proxy
    artist = association_proxy("shows", "artist")

    def __repr__(self):
        return f'<Venue id: {self.id}, Venue name: {self.name}>'

# Define Shows table as the association tableobject for Artist and Venue class (many-to-many relation)

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    start_time = db.Column(db.DateTime())

    artist = db.relationship(Artist, backref="shows")
    venue = db.relationship(Venue, backref="shows")

    def __repr__(self):
        return f'<Show id: {self.id}, Artist id: {self.artist_id}, Venue id: {self.venue_id}, Show starttime: {self.start_time}>'


