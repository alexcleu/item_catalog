from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Vocalband, Musicsheet, User

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Alex Acaproject"

app = Flask(__name__)

engine = create_engine('sqlite:///vocalbandmusic.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase+string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output
    
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['credentials']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/vocalbands/JSON/')
def vocalbandJSON():
    vocalbands = session.query(Vocalband).all()
    return jsonify(Vocalband=[i.serialize for i in vocalbands])

@app.route('/vocalband/<int:vocalband_id>/musicsheet/JSON/')
def VocalbandMusicJSON(vocalband_id):
    vocalband = session.query(Vocalband).filter_by(id=vocalband_id).one()
    musics = session.query(Musicsheet).filter_by(vocalband_id=vocalband_id)
    return jsonify(Musicsheets = [i.serialize for i in musics])
    
@app.route('/vocalband/<int:vocalband_id>/musicsheet/<int:musicsheet_id>/JSON/')
def VocalbandMusicsheetJSON(vocalband_id, musicsheet_id):
    musics = session.query(Musicsheet).filter_by(id=musicsheet_id).one()
    return jsonify(music = musics.serialize)
    
@app.route('/')
@app.route('/vocalbands/')
def showVocalband():
  vocalbands = session.query(Vocalband).all()
  return render_template('vocalband.html', vocalbands=vocalbands)

@app.route('/vocalband/new', methods = ['GET', 'POST'])    
def newVocalband():
    if request.method =='POST':
        newVocalband = Vocalband(name=request.form['name'])
        session.add(newVocalband)
        session.commit()
        return redirect(url_for('showVocalband'))
    else:
        return render_template('newVocalband.html')
    

@app.route('/vocalband/<int:vocalband_id>/edit', methods=['GET', 'POST'])
def editVocalband(vocalband_id):
    editVocalband = session.query(Vocalband).filter_by(id=vocalband_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editVocalband.name = request.form['name']
        session.add(editVocalband)
        session.commit()
        return redirect(url_for('showVocalband'))
    else:
        return render_template('editVocalband.html', vocalband=editVocalband)
        
    return "this is the edit vocal band page for number %s!" % vocalband_id

@app.route('/vocalband/<int:vocalband_id>/delete', methods=['GET', 'POST'])
def deleteVocalband(vocalband_id):
    deletedVocalband = session.query(Vocalband).filter_by(id=vocalband_id).one()
    if request.method == 'POST':
        session.delete(deletedVocalband)
        session.commit()
        return redirect(url_for('showVocalband'))
    else:
        return render_template('deleteVocalband.html', vocalband= deletedVocalband)


@app.route('/vocalband/<int:vocalband_id>/')
@app.route('/vocalband/<int:vocalband_id>/music')
def vocalbandmusic(vocalband_id):
    vocalband = session.query(Vocalband).filter_by(id=vocalband_id).one()
    musics = session.query(Musicsheet).filter_by(vocalband_id=vocalband.id)
    return render_template('musicsheet.html', vocalband=vocalband, musics=musics)
    
@app.route('/vocalband/<int:vocalband_id>/new', methods=['GET', 'POST'])
def createMusicsheet(vocalband_id):
    if request.method == 'POST':
        newMusic = Musicsheet(name=request.form['name'],
                              vocalband_id = vocalband_id,
                              needs_beatbox = request.form['beatbox'],
                              vocal_part= request.form['voicepart'])
        
        session.add(newMusic)
        session.commit()
        return redirect(url_for('vocalbandmusic', vocalband_id=vocalband_id))

    else:
        return render_template('newmusicsheet.html', vocalband_id=vocalband_id)

@app.route('/vocalband/<int:vocalband_id>/<int:musicsheet_id>/edit',
            methods=['GET', 'POST'])
def editMusicsheet(vocalband_id, musicsheet_id):
    editMusic = session.query(Musicsheet).filter_by(id=musicsheet_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editMusic.name = request.form['name']
        
        session.add(editMusic)
        session.commit()
        return redirect(url_for('vocalbandmusic', vocalband_id = vocalband_id))
    else:
        return render_template(
            'editMusicsheet.html', vocalband_id=vocalband_id, musicsheet_id =
            musicsheet_id, musicsheet = editMusic)
        

@app.route('/vocalband/<int:vocalband_id>/<int:musicsheet_id>/delete',
            methods=['GET', 'POST'])
def deleteMusicsheet(vocalband_id, musicsheet_id):
    deletedMusic = session.query(Musicsheet).filter_by(id=musicsheet_id).one()
    if request.method == 'POST':
        
        session.delete(deletedMusic)
        session.commit()
        return redirect(url_for('vocalbandmusic', vocalband_id = vocalband_id))
    else:
        return render_template('deletemusicsheet.html', music = deletedMusic)
            

def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None



def getUserInfo(user_id):
    user = session.query(User).filter_by(id =user_id).one()
    return user
    
def createUser(login_session):
    newUser = User(name = login_session['username'], email= login_session['email'],
    picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host ='0.0.0.0', port = 5000)
