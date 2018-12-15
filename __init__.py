from flask import Flask, request, redirect, url_for, render_template,session,flash
from flask_table import Table, Col, DatetimeCol
import tweepy #https://github.com/tweepy/tweepy
import csv
import os
#import MySQLdb
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = 'honeypots'


#Generate session key
#app.secret_key = os.random(24)

#Database credentials
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/testdb'




db = SQLAlchemy(app)


#Twitter API credentials
consumer_key = "Q1GlAHCqg1rU32RKe18UPugXx"
consumer_secret = "DkbpHpBCHU90Jh3wx6AYsblJpKqDmmkDnyH5whpYYPGCH4uY7i"
access_key = "338765001-pd9Rj6irx6D8j1WA48lKlWp5HyQHLAzpyKeAIgyb"
access_secret = "qAvOlDuOS0PrBeHObNqYHYk0eeK2ymxgRqOPJ0RnFilev"

#authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

#declare models
class User(db.Model):
	__tablename__ = 'User'
	id = db.Column('id', db.Integer, primary_key =True)
	username = db.Column('username', db.VARCHAR(255))
	password = db.Column('pwd', db.VARCHAR(255))
	tweets = db.relationship('Tweet', backref = 'User', lazy = True)

class Tweet(db.Model):
	__tablename__ = 'Tweet'
	id = db.Column('id', db.Integer, primary_key = True)
	create_date = db.Column('create_date', db.DateTime)
	text = db.Column('text', db.VARCHAR(140))
	retweet_count = db.Column('retweet_count', db.Integer)
	favorite_count = db.Column('favorite_count', db.Integer)
	user_id = db.Column('user_id', db.Integer, db.ForeignKey('User.id'))

class TweetTable(Table):
	id = Col('id')
	create_date = DatetimeCol('create_date')
	text = Col('text')
	retweet_count = Col('retweet_count')
	favorite_count = Col('favorite_count')






@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'POST':

		username = request.form.get('un')
		password = request.form.get('pw')

		data = User.query.filter_by(username=username,password=password).first()
		if data is not None:

			session['username'] = username
			return redirect(url_for('userpage'))


		flash('username or password is incorrect')
		return render_template('index.html')


	return render_template('index.html')

@app.route('/register', methods = ['GET', 'POST'])
def success():
	if request.method == 'POST':

		username = request.form.get('un')
		password = request.form.get('pw')

		#check if username is already set_access_taken
		check = User.query.filter_by(username = username).first()
		if check is not None:
			flash('username already taken')
			return render_template('register.html')

		if not password:
			flash('please enter a password')
			return render_template('register.html')

		if not username:
			flash('please enter a username')
			return render_template('register.html')

		new_user = User(username = username,password = password)

		db.session.add(new_user)
		db.session.commit()
		return redirect(url_for('login'))

	return render_template('register.html')



@app.route('/userpage', methods = ['GET', 'POST'])
def userpage():
	if request.method == 'POST':

		#current user
		curr_user = User.query.filter_by(username = session['username']).first()

		#print curr_user.id

		username = request.form.get('tun')

		#initialize a list to hold all the tweepy Tweet
		alltweets = []

	  	#make initial request for most recent tweets (200 is the maximum allowed count)
	  	new_tweets = api.user_timeline(screen_name = username,count=200)

		#save most recent tweets
	  	alltweets.extend(new_tweets)

	  	#save the id of the oldest tweet less one
	  	oldest = alltweets[-1].id - 1

		#keep grabbing tweets until there are no tweets left to grab
		while len(new_tweets) > 0:

			#print "getting tweets before %s" % (oldest)

			#all subsiquent requests use the max_id param to prevent duplicates
			new_tweets = api.user_timeline(screen_name = username,count=200,max_id=oldest)

			#save most recent tweets
			alltweets.extend(new_tweets)

			#update the id of the oldest tweet less one
			oldest = alltweets[-1].id - 1

		for tweet in alltweets:

			new_tweet = Tweet(id = tweet.id_str, create_date = tweet.created_at, text = tweet.text.encode("utf-8"), retweet_count = tweet.retweet_count, favorite_count = tweet.favorite_count, user_id = curr_user.id)
			db.session.add(new_tweet)
			db.session.commit()


		return render_template('userpage.html', data = alltweets)

	return render_template('userpage.html')



@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('login'))

if __name__ == "__main__":
	app.run(debug = True)
