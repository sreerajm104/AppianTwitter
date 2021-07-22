from flask import Flask,request,render_template,send_file
import tweepy
from textblob import TextBlob
from wordcloud import WordCloud
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from PIL import Image
import seaborn as sns
import time

# Assign API Key and authenticate tweepy
consumer_key = "Nj3kha2CYN94LBW2M54ezRPhO"
consumer_secret = "4PqwK44LqtxNmhxFbOQC3EwJockvcLZA5bLvmVAy9EjH89Ia1y"
access_token = "1108075687380836352-5pDD452FKejmf9GXo3hiTNFqwEGtYF"
access_token_secret = "JaOVt7P3GTx0oX65OrOPzqRwVRNKsYErt3NXeuMnc1w2z"

#Authentication

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
#Create API object
api = tweepy.API(auth,wait_on_rate_limit = True)

def Show_Tweets(handler_id):    
    try:         
        posts = api.user_timeline(screen_name= handler_id,count = 100, lang='en',tweet_mode="extended")                
        df = pd.DataFrame([tweet.full_text for tweet in posts], columns=['Tweets'])
        def cleantext(text):
            
            text = re.sub('@[A-Za-z0–9]+', '', text) #Removing @mentions
            text = re.sub('#', '', text) # Removing '#' hash tag
            text = re.sub('RT[\s]+', '', text) # Removing RT
            text = re.sub('https?:\/\/\S+', '', text) # Removing hyperlink
            
            return text
        
        df['Tweets'] = df['Tweets'].apply(cleantext)     
        def getSubjectivity(text):
            return TextBlob(text).sentiment.subjectivity
        
        df["Subjectivity"] = df["Tweets"].apply(getSubjectivity)
        
        def getPolarity(text):
            return  TextBlob(text).sentiment.polarity
        
        df["Polarity"] = df["Tweets"].apply(getPolarity)
        
        def captureAnalysis(score):
            if score < 0:
                return "Negative"
            elif score == 0:
                return "Neutral"
            else:
                return "Positive"
        df["Analysis"] = df["Polarity"].apply(captureAnalysis)
        data_dict = df.to_dict()
        return data_dict
    except:
        notweet = list()
        return notweet
    
    
def World_Cloud(handler_id):
    posts = api.user_timeline(screen_name= handler_id,count = 100, lang='en',tweet_mode="extended")                
    df = pd.DataFrame([tweet.full_text for tweet in posts], columns=['Tweets'])
    def cleantext(text):
        
        text = re.sub('@[A-Za-z0–9]+', '', text) #Removing @mentions
        text = re.sub('#', '', text) # Removing '#' hash tag
        text = re.sub('RT[\s]+', '', text) # Removing RT
        text = re.sub('https?:\/\/\S+', '', text) # Removing hyperlink
        
        return text
    
    df['Tweets'] = df['Tweets'].apply(cleantext)
    
    allwords = ' '.join([twt for twt in df["Tweets"]])
    worldCloud = WordCloud(width=800,height = 500,random_state=21,max_font_size=120).generate(allwords)
    # plt.imshow(worldCloud, interpolation="bilinear")
    # plt.axis('off')
    # plt.savefig("WC.JPEG")
    # imgopen = Image.open("WC.JPEG")
    # imgopen = worldCloud.to_file("WC.JPEG")
    return worldCloud


#Run the Flask App
app = Flask(__name__)

@app.route('/')
def home():    
    return render_template('index.html')

# 	return "Tweet Analyzer"

@app.route('/gettweets',methods=['POST'])
def getTweets():
    if request.method == 'POST':        
        handler_id = request.args.get('handler_id')
        displaytweet = Show_Tweets(handler_id)
        return displaytweet

@app.route('/wordcloud',methods=['POST'])
def wordcloud():
    if request.method == 'POST':        
        handler_id = request.args.get('handler_id')
        imgDisp = World_Cloud(handler_id)
        imgDisp.to_file("WC.JPEG")
        return send_file("WC.JPEG", mimetype='image/gif',as_attachment=True)
    
if __name__ == '__main__':
	app.run(debug=True)