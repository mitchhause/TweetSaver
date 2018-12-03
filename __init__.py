from flask import Flask, request, redirect, url_for, render_template,session
import tweepy #https://github.com/tweepy/tweepy
import csv
import os
#import MySQLdb
from flask_mysqldb import MySQL

app = Flask(__name__)

mysql = MySQL(app)
#Generate session key
#app.secret_key = os.random(24)

#Database credentials
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'testdb'


#Twitter API credentials
consumer_key = "Q1GlAHCqg1rU32RKe18UPugXx"
consumer_secret = "DkbpHpBCHU90Jh3wx6AYsblJpKqDmmkDnyH5whpYYPGCH4uY7i"
access_key = "338765001-pd9Rj6irx6D8j1WA48lKlWp5HyQHLAzpyKeAIgyb"
access_secret = "qAvOlDuOS0PrBeHObNqYHYk0eeK2ymxgRqOPJ0RnFilev"

@app.route('/success/<name>')
def success(name):
	return 'welcome %s' % name

@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'POST':

		#session.['user'] = request.form['nm']
		user = request.form['nm']
		#session.['password'] = request.form['pw']
		return redirect(url_for('get_all_tweets', name = user))

	return render_template('index.html')

@app.route('/get_all_tweets/<name>')
def get_all_tweets(name):

    cur = mysql.connection.cursor()
    #authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    #initialize a list to hold all the tweepy Tweets
    alltweets = []

    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = name,count=200)

    #save most recent tweets
    alltweets.extend(new_tweets)

    #save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    #keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        #print "getting tweets before %s" % (oldest)

        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = name,count=200,max_id=oldest)

        #save most recent tweets
        alltweets.extend(new_tweets)

        #update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

    #    print "...%s tweets downloaded so far" % (len(alltweets))
	for tweet in alltweets:

		cur.execute(
			"""INSERT INTO Tweets (id, create_date, text, retweet_count, favorite_count)
			VALUES (%s, %s, %s, %s, %s)""",
			[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8"), tweet.retweet_count,tweet.favorite_count])

		mysql.commit();

	return render_template('success.html')

if __name__ == "__main__":
	app.run(debug = True)
