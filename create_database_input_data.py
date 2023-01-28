## Support file to create test data in the database following the examples

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

# Obtain local database configuration from config.py
app.config.from_object('config')

db = SQLAlchemy(app)

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

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
#  Generate Venues database entries
#----------------------------------------------------------------------------#

venue_1 = Venue(name = 'The Musical Hop', city = 'San Francisco', state = 'CA',
    genres = ['Jazz', 'Reggae', 'Swing', 'Classical', 'Folk'],
    address = '1015 Folsom Street', phone = '123-123-1234', website = 'https://www.themusicalhop.com',
    facebook_link = 'https://www.facebook.com/TheMusicalHop', seeking_talent = True,
    seeking_description = 'We are on the lookout for a local artist to play every two weeks. Please call us.',
    image_link = 'https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60')

venue_2 = Venue(name = 'The Dueling Pianos Bar', city = 'New York', state = 'NY',
    genres = ['Classical', 'R&B', 'Hip-Hop'],
    address = '335 Delancey Street', phone = '914-003-1132', website = 'https://www.theduelingpianos.com',
    facebook_link = 'https://www.facebook.com/theduelingpianos', seeking_talent = False,
    seeking_description = '',
    image_link = 'https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80')

venue_3 = Venue(name = 'Park Square Live Music & Coffee', city = 'San Francisco', state = 'CA',
    genres = ['Rock n Roll', 'Jazz', 'Classical', 'Folk'],
    address = '34 Whiskey Moore Ave', phone = '415-000-1234', website = 'https://www.parksquarelivemusicandcoffee.com',
    facebook_link = 'https://www.facebook.com/ParkSquareLiveMusicAndCoffee', seeking_talent = False,
    seeking_description = '',
    image_link = 'https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80')

#----------------------------------------------------------------------------#
#  Generate Artist database entries
#----------------------------------------------------------------------------#

artist_4 = Artist(name = 'Guns N Petals', city = 'San Francisco', state = 'CA',
    genres = ['Rock n Roll'],
    phone = '326-123-5000', website = 'https://www.gunsnpetalsband.com',
    facebook_link = 'https://www.facebook.com/GunsNPetals', seeking_venue = True,
    seeking_description = 'Looking for shows to perform at in the San Francisco Bay Area!',
    image_link = 'https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80')

artist_5 = Artist(name = 'Matt Quevedo', city = 'New York', state = 'NY',
    genres = ['Jazz'],
    phone = '300-400-5000', website = '',
    facebook_link = 'https://www.facebook.com/mattquevedo923251523', seeking_venue = False,
    seeking_description = '',
    image_link = 'https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80')

artist_6 = Artist(name = 'The Wild Sax Band', city = 'San Francisco', state = 'CA',
    genres = ['Jazz', 'Classical'],
    phone = '415-000-123432-325-5432', website = '',
    facebook_link = '', seeking_venue = False,
    seeking_description = '',
    image_link = 'https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80')

#----------------------------------------------------------------------------#
#  Generate Show database entries
#----------------------------------------------------------------------------#

show_1 = Show(artist_id = 1, venue_id = 1, start_time = '2019-05-21T21:30:00.000Z')
show_2 = Show(artist_id = 2, venue_id = 3, start_time = '2019-06-15T23:00:00.000Z')
show_3 = Show(artist_id = 3, venue_id = 3, start_time = '2035-04-01T20:00:00.000Z')
show_4 = Show(artist_id = 3, venue_id = 3, start_time = '2035-04-08T20:00:00.000Z')
show_5 = Show(artist_id = 3, venue_id = 3, start_time = '2035-04-15T20:00:00.000Z')

# Execute the insertion commands
with app.app_context():
    db.session.add(venue_1)
    db.session.add(venue_2)
    db.session.add(venue_3)
    db.session.add(artist_4)
    db.session.add(artist_5)
    db.session.add(artist_6) 
    db.session.add(show_1)
    db.session.add(show_2)
    db.session.add(show_3)
    db.session.add(show_4)
    db.session.add(show_5) 
    db.create_all()
    db.session.commit()


