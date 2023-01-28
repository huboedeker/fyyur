#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
import logging
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
# Obtaining models drom separate file
#from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

# Obtain local database configuration from config.py
app.config.from_object('config')

db = SQLAlchemy(app)
db.init_app(app)

# Prepare migrations
migrate = Migrate(app, db)

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
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  # Initialize the current time and the data dictionary to be passed back  
  time_now = datetime.now()
  data = []

  # Get the venues according to city and state
  venue_list = Venue.query.distinct(Venue.city, Venue.state).all()

  # Prepare the city / state part of the entry by looping through venue list
  for venue_item in venue_list:
      city_state_entry = {
          "city": venue_item.city,
          "state": venue_item.state
      }

      # For the specifiy city / state combination, add the id / name / show parts 
      venues = Venue.query.filter_by(city=venue_item.city, state=venue_item.state).all()

      # Format the dictionary entry by the initializing the format string, looping through each entry of matching venue
      # and adding to dictionary entry
      venues_part = []

      for venue in venues:
          # Create a list of the shows in the specific venue
          venue_shows = Show.query.filter_by(venue_id=venue.id).all()
          upcoming_show_count = 0

          # Loop through shows and check whether start time is in the future    
          for show in venue_shows:
              if show.start_time > time_now:
                  upcoming_show_count += 1

          # Create the venue data part
          venues_part.append({
              "id": venue.id,
              "name": venue.name,
              "num_upcoming_shows": upcoming_show_count
              })
        
      city_state_entry["venues"] = venues_part

      # Append the completed entry 
      data.append(city_state_entry)

  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # search for venues, case-insensitive

    # Get the search string from the search form request
    search_term = request.form.get('search_term', '').strip()

 # Initialize the current time and the search result to be passed back  
    time_now = datetime.now() 
    count = 0
    search_result = []

    # Get the matching venues from the list by using alike for case insensitive search + wildcard characters around it
    venues_search_list = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()

    # Loop through the list of venues to produce the proper entries
    for venue in venues_search_list:
        # Count entries and prepare the artist entries which can be directly obtained
        count +=1
        search_entry = {
            "id": venue.id,
            "name": venue.name
        }

        #Initialize future show count
        upcoming_show_count = 0

        # Create a list of the shows for the specific venue
        venue_shows = Show.query.filter_by(venue_id=venue.id).all()
          
        # Loop through shows and check whether start time is in the future    
        for show in venue_shows:
            if show.start_time > time_now:
                upcoming_show_count += 1
        
        search_entry["num_upcoming_shows"] = upcoming_show_count

        # Append the show-related data to search result
        search_result.append(search_entry)
        
    # Create the response entry
    response = {
        "count": count,
        "data": search_result
    }
 
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  # Initialize the current time and the data dictionary to be passed back  
  time_now = datetime.now() 
  data = []

  # Get the requested venues from the list
  venue = Venue.query.get(venue_id)

  # Check if venue returned a valid statement to catch invalid requests

  if not venue:
      # Cause some controlled reaction and redirect to index location
      return redirect(url_for('index'))
  else:
      # Prepare the venue entries which can be directly obtained
      data = {
          "id": venue.id,
          "name": venue.name,
          # Genres need to be converted to a list to work with the template
          "genres": venue.genres[1:-1].split(','),
          "address": venue.address,
          "city": venue.city,
          "state": venue.state,
          "phone": venue.phone,
          "website": venue.website,
          "facebook_link": venue.facebook_link,
          "seeking_talent": venue.seeking_talent,
          "seeking_description": venue.seeking_description,
          "image_link": venue.image_link
      }

      #Initialize past and future show entries
      past_show_part = []
      upcoming_show_part = []
      upcoming_show_count = 0
      past_show_count = 0

      # Create a list of the shows in the specific venue
      venue_shows = Show.query.filter_by(venue_id=venue.id).all()
          
      # Loop through shows and check whether start time is in the future    
      for show in venue_shows:
          if show.start_time > time_now:
              upcoming_show_count += 1
              upcoming_show_part.append({
                  "artist_id": show.artist_id,
                  "artist_name": show.artist.name,
                  "artist_image_link": show.artist.image_link,
                  "start_time": format_datetime(str(show.start_time), format='medium')
              })

          else:
              past_show_count += 1
        
              past_show_part.append({
                  "artist_id": show.artist_id,
                  "artist_name": show.artist.name,
                  "artist_image_link": show.artist.image_link,
                  "start_time": format_datetime(str(show.start_time), format='medium')
              })
        
      # Append the show-related data to data
        
      data["upcoming_shows"] = upcoming_show_part
      data["upcoming_shows_count"] = upcoming_show_count
      data["past_shows"] = past_show_part
      data["past_shows_count"] = past_show_count

      return render_template('pages/show_venue.html', venue=data)
 

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  # As defined in forms.py
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # As defined in forms.py
  form = VenueForm(request.form)

  # Obtain the individual data from the form

  name = request.form['name']
  city= request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  image_link = request.form['image_link']
  genres = request.form.getlist('genres') # Use getlist here due to multiple entries
  facebook_link =request.form['facebook_link']
  website = request.form['website_link']
  # The string from the form needs to be converted to a Boolean since only when checked value is returned by request.form
  if 'seeking_talent' in request.form:
    seeking_talent = True
  else:
    seeking_talent = False
  seeking_description  = request.form['seeking_description']
 
  # Perform the form validation run
  if not form.validate():
    flash( form.errors )
    
    return redirect(url_for('create_venue_submission'))

  # Initialize error flag to false
  error = False

  try:
    # Try to create a new database entry with the provided forms data 
    new_venue_entry = Venue(name=name, city=city, state=state, address=address, phone = phone,
                image_link=image_link, genres= genres, facebook_link=facebook_link, website=website,
                seeking_talent=seeking_talent, seeking_description=seeking_description
                )

    db.session.add(new_venue_entry)
    db.session.commit()
  except:
    # Standard procedure for error handling
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  # on successful db insert, flash success
  if error == False:
    flash('Venue ' + name + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
   # Initialize error flag to false
    error = False

    # Try to get json description string and commit to database
    try:
        # Get the database item to be deleted
        delvenue = Venue.query.get(venue_id)
        # Store the name for the error message below
        delvenue_name = delvenue.name
        db.session.delete(delvenue)
        db.session.commit()
    # In case try fails set error to true and call rollback 
    except:
        error = True
        db.session.rollback()
    # At the end, close connection and refresh overall page
    finally:
        db.session.close()
    if error == True:
        flash('An error occurred. Venue ' + delvenue_name + ' could not be deleted.')
        abort(500)
    else:
        return jsonify({'Deletion success': True})



  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

# Initialize the data dictionary to be passed back  
  data = []

  # Get all artists from the list (sorted by artist name)
  artist_list = Artist.query.order_by(Artist.name).all()

  # Prepare the id and artist entry by looping through venue list
  for artist_item in artist_list:
      artist_entry = {
          "id": artist_item.id,
          "name": artist_item.name
      }

      # Append the entry to the data 
      data.append(artist_entry)

  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # search for artists, case-insensitive

    # Get the search string from the search form request
    search_term = request.form.get('search_term', '').strip()

    # Initialize the current time and the search result to be passed back  
    time_now = datetime.now() 
    count = 0
    search_result = []

    # Get the matching artists from the list by using alike for case insensitive search + wildcard characters around it
    artists_search_list = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()

    # Loop through the list of artists to produce the proper entries
    for artist in artists_search_list:
        # Count entries and prepare the artist entries which can be directly obtained
        count +=1
        search_entry = {
            "id": artist.id,
            "name": artist.name
        }

        #Initialize future showcount
        upcoming_show_count = 0

        # Create a list of the shows for the specific artist
        artist_shows = Show.query.filter_by(artist_id=artist.id).all()
          
        # Loop through shows and check whether start time is in the future    
        for show in artist_shows:
            if show.start_time > time_now:
                upcoming_show_count += 1
        
        search_entry["num_upcoming_shows"] = upcoming_show_count

        # Append the show-related data to search result
        search_result.append(search_entry)
        
    # Create the response entry
    response = {
        "count": count,
        "data": search_result
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given 
  
    # Initialize the current time and the data dictionary to be passed back  
    time_now = datetime.now() 
    data = []

    # Get the requested artist from the list
    artist = Artist.query.get(artist_id)

    # Check if artist returned a valid statement to catch invalid requests

    if not artist:
        # Cause some controlled reaction and redirect to index location
        redirect(url_for('index'))
    else:
        # Prepare the artist entries which can be directly obtained
        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres[1:-1].split(','),
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link
        }

        #Initialize past and future show entries
        past_show_part = []
        upcoming_show_part = []
        upcoming_show_count = 0
        past_show_count = 0

        # Create a list of the shows for the specific artist
        artist_shows = Show.query.filter_by(artist_id=artist.id).all()
          
        # Loop through shows and check whether start time is in the future    
        for show in artist_shows:
            if show.start_time > time_now:
                upcoming_show_count += 1

                upcoming_show_part.append({
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": format_datetime(str(show.start_time), format='medium')
                })

            else:
                past_show_count += 1
        
                past_show_part.append({
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": format_datetime(str(show.start_time), format='medium')
                })
        
        # Append the show-related data to data
        
        data["upcoming_shows"] = upcoming_show_part
        data["upcoming_shows_count"] = upcoming_show_count
        data["past_shows"] = past_show_part
        data["past_shows_count"] = past_show_count

        return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  # Get the existing artist from the database
  artist = Artist.query.get(artist_id)

  # Polulate the form with the queried artist data
  form = ArtistForm(obj=artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
 
  # Get the existing venue from the database
  venue = Venue.query.get(venue_id)

  # Polulate the form with the queried artist data
  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
# As defined in forms.py
  form = ArtistForm(request.form)

  # Obtain the individual data from the form

  name = request.form['name']
  city= request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  image_link = request.form['image_link']
  genres = request.form.getlist('genres') # Use getlist here due to multiple entries
  facebook_link =request.form['facebook_link']
  website = request.form['website_link']
  # The string from the form needs to be converted to a Boolean since only when checked value is returned by request.form
  if 'seeking_venue' in request.form:
    seeking_venue = True
  else:
    seeking_venue = False
  seeking_description  = request.form['seeking_description']
 
  # Perform the form validation run
  if not form.validate():
    
    flash( form.errors )
    return redirect(url_for('create_venue_submission'))

  # Initialize error flag to false
  error = False

  try:
    # Get the artist entry to update from the database
    artist = Artist.query.get(artist_id)

    # Overwrite the existing venue data fields with the data from the form

    artist.name = name
    artist.city = city  
    artist.state = state
    artist.phone = phone
    artist.image_link = image_link
    artist.genres = genres
    artist.facebook_link = facebook_link
    artist.website = website
    artist.seeking_venue = seeking_venue
    artist.seeking_description = seeking_description
   
    db.session.commit()
  except:
    # Standard procedure for error handling
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  # on successful db update, flash success
  if error == False:
    flash('Artist ' + name + ' was successfully updated!')
  else:
    flash('An error occurred. Artist ' + name + ' could not be updated.')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
# As defined in forms.py
  form = VenueForm()

  # Obtain the individual data from the form

  name = request.form['name']
  city= request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  image_link = request.form['image_link']
  genres = request.form.getlist('genres') # Use getlist here due to multiple entries
  facebook_link =request.form['facebook_link']
  website = request.form['website_link']
  # The string from the form needs to be converted to a Boolean since only when checked value is returned by request.form
  if 'seeking_talent' in request.form:
    seeking_talent = True
  else:
    seeking_talent = False
  seeking_description  = request.form['seeking_description']
 
  # Perform the form validation run
  """
  if not form.validate():
    #flash('The entries were not correctly filled, the following errors ocurred:' form.errors )
    flash( form.errors )
    return redirect(url_for('create_venue_submission'))
  """
  # Initialize error flag to false
  error = False

  try:
    # Get the venue entry to update from the database
    venue = Venue.query.get(venue_id)

    # Overwrite the existing venue data fields with the data from the form

    venue.name = name
    venue.city = city  
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.image_link = image_link
    venue.genres = genres
    venue.facebook_link = facebook_link
    venue.website = website
    venue.seeking_talent = seeking_talent
    venue.seeking_description = seeking_description
   
    db.session.commit()
  except:
    # Standard procedure for error handling
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  # on successful db update, flash success
  if error == False:
    flash('Venue ' + name + ' was successfully updated!')
  else:
    flash('An error occurred. Venue ' + name + ' could not be updated.')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
# As defined in forms.py
  form = ArtistForm()

  # Obtain the individual data from the form

  name = request.form['name']
  city= request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  image_link = request.form['image_link']
  genres = request.form.getlist('genres') # Use getlist here due to multiple entries
  facebook_link =request.form['facebook_link']
  website = request.form['website_link']
  # The string from the form needs to be converted to a Boolean since only when checked value is returned by request.form
  if 'seeking_venue' in request.form:
    seeking_venue = True
  else:
    seeking_venue = False
  seeking_description  = request.form['seeking_description']
 
  # Perform the form validation run

  #if not form.validate():
    #flash('The entries were not correctly filled, the following errors ocurred:' form.errors )
    #flash( form.errors )
    #return redirect(url_for('create_artist_submission'))

  # Initialize error flag to false
  error = False

  try:
    # Try to create a new database entry with the provided forms data 

    new_artist_entry = Artist(name=name, city=city, state=state, phone = phone,
                image_link=image_link, genres=genres, facebook_link=facebook_link, website=website,
                seeking_venue=seeking_venue, seeking_description=seeking_description
                )

    db.session.add(new_artist_entry)
    db.session.commit()
  except:
    # Standard procedure for error handling
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  # on successful db insert, flash success
  if error == False:
    flash('Artist ' + name + ' was successfully listed!')
  else:
    flash('An error occurred. Artist ' + name + ' could not be listed.')
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows
    

    # Initialize the data dictionary to be passed back  
    data = []

    # Get all shows from the list
    show_list = Show.query.all()

     # Prepare the show entries by looping through show list
    for show_item in show_list:
        show_entry = {
          "venue_id": show_item.venue.id,
          "venue_name": show_item.venue.name,
          "artist_id": show_item.artist.id,
          "artist_name": show_item.artist.name,
          "artist_image_link": show_item.artist.image_link,
          "start_time": format_datetime(str(show_item.start_time), format='medium')
            }

        # Append the entry to the data
        data.append(show_entry)

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
# As defined in forms.py
  form = ShowForm()

  # Obtain the individual data from the form

  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']
 
  # Perform the form validation run
  """
  if not form.validate():
    #flash('The entries were not correctly filled, the following errors ocurred:' form.errors )
    flash( form.errors )
    return redirect(url_for('create_venue_submission'))
  """
  # Initialize error flag to false
  error = False

  try:
    # Try to create a new database entry with the provided forms data 
    new_show_entry = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time
                )

    db.session.add(new_show_entry)
    db.session.commit()
  except:
    # Standard procedure for error handling
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  # on successful db insert, flash success
  if error == False:
    flash('Show was successfully listed!')
  else:
    flash('An error occurred. Show could not be listed.')
  
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
