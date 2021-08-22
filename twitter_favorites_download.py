#!/usr/bin/env python

import sys
if sys.version_info[0] < 3:
    raise "[!] Error: Must be using Python 3"

try:
        print("(c) Joshua Smith - Cornerstone Security")
        print("https://www.cornerstonesec.com")
        print("")
        print("[*] Starting download of Twitter Favorites")
        import twitter
        import csv 
        import time
        from bs4 import BeautifulSoup
        import requests
        import datetime
        import os
        import pickle
        import argparse
        import magic
        import configparser
except Exception as e:
        print("[!] Error: %s" % e)
        print("[?] Have you run 'sudo pip3 install -r requirements.txt'? ")
        print("[?] You have to 'sudo install python3-pip' to have pip3 available. ")
        sys.exit()

# Left for when we need to take some command line arguments
#parser = argparse.ArgumentParser(description='Download Twitter Favorites')
#parser.add_argument('-f','--folder', help='Folder to create and download Twitter favorites into', required=True)
#args = parser.parse_args()

try:
        config = configparser.ConfigParser()
        config_file = 'config.file'
        if os.path.exists(config_file):
                config.read(config_file)
                try:
                        folder_destination = config.get('settings', 'folder_destination')
                        consumer_key = config.get('api_keys', 'consumer_key')
                        consumer_secret = config.get('api_keys', 'consumer_secret')
                        access_token_key = config.get('api_keys', 'access_token_key')
                        access_token_secret = config.get('api_keys', 'access_token_secret')
                        if not (consumer_key or consumer_secret or access_token_key or access_token_secret):
                            print("[!] Error: Your Twitter API keys are not entered into config.file")
                            sys.exit()
                except Exception as e:
                        print("[!] Error: %s" % e)
                        sys.exit()

        else:
                print("[!] Error: Missing config.file")
                sys.exit()
except Exception as e:
        print("[!] Error: %s" % e)
        sys.exit()

directory_output = folder_destination

# Define your Twitter favorites class structure
class twitter_favorite:
        def __init__(self, tw_id, tw_full_text, tw_media, tw_original_media, tw_urls, tw_original_urls, tw_source, tw_screen_name, tw_user, tw_time):
                self.id = tw_id
                self.full_text = tw_full_text
                self.media = tw_media
                self.media_original = tw_original_media
                self.urls = tw_urls
                self.urls_original = tw_original_urls
                self.source = tw_source
                self.screen_name = tw_screen_name
                self.user = tw_user
                self.time = tw_time


timestamp = datetime.datetime.now().strftime('%Y%m%d.%H%M%S')

if not os.path.exists(directory_output):
    os.makedirs(directory_output)

api = twitter.Api(consumer_key=consumer_key, \
        consumer_secret=consumer_secret, \
        access_token_key=access_token_key, \
        access_token_secret=access_token_secret, \
        tweet_mode='extended', \
        sleep_on_rate_limit=True)

tweet_exists = True
try:
        latest_favorite_id = api.GetFavorites(count=1)
except Exception as e:
        print("[!] Error: %s" % e)
        print("[?] Are you sure your API keys are correct in the config.file?")
        sys.exit()

tweet_id = latest_favorite_id[0].id
tweet_count = 1
tweets_complete_current = []
tweets_complete_historical = []
tweets_complete = []

file_tweet_index = directory_output + "/tweets.index"

if os.path.exists(file_tweet_index):
        try:
                tweets_complete = pickle.load(open(file_tweet_index, "rb"))
        except Exception as e:
                print("[!] Error opening index file: %s" % e )

while(tweet_exists):
        try:
                # Calculate how many API requests we have remaining, debugging purporses only
                requests_remaining = api.rate_limit.resources.get('favorites').get('/favorites/list')['remaining']
                print(requests_remaining)

                tweets = api.GetFavorites(max_id=tweet_id, count=200)

                # Logic to remove first tweet of the favorites to avoid duplicates
                # unless it is truly the first tweet we have pulled
                if tweet_count > 3:
                        if len(tweets) > 1:
                                tweets.pop(0)
                
                # Logic to handle when there are no more tweets to pull
                if len(tweets) == 1:
                        if tweet_count > 1:
                                tweet_exists = False
                                break

                # Iterate over tweets                 
                for tweet in tweets:
                        
                        # If Tweet ID isn't in the list of tweets_complete_current do work
                        if tweet.id not in [ti.id for ti in tweets_complete]:
                                print("Tweet ID: %s\t\tTweet Count: %s\t\tStatus: New" % (tweet.id, tweet_count))
                                tweet_id = tweet.id
                                tweet_count += 1
                                tweet_full_text = tweet.full_text
                                #tweet_full_text = tweet.full_text.encode("utf-8")
                                tweet_media = tweet.media
                                tweet_media_all = []
                                tweet_original_media_all = []
                                # Iterate over any media Tweet contains
                                if tweet_media:
                                        directory_media = directory_output + "/" + str(tweet.id) + "/media/"
                                        if not os.path.exists(directory_media):
                                                os.makedirs(directory_media)
                                        for media in tweet_media:
                                                try:
                                                        r = requests.get(media.media_url)
                                                        tweet_media_unique = media.media_url.split('/')[-1]
                                                        file_media = str(directory_media) + str(tweet_media_unique) 
                                                        #tweet_original_media_all.append(media.media_url.encode("utf-8"))
                                                        tweet_original_media_all.append(media.media_url)
                                                        tweet_media_all.append(file_media)
                                                        with open(file_media, "wb") as f:
                                                                f.write(r.content)
                                                except Exception as e:
                                                        print("Error: %s" % e)

                                tweet_urls = tweet.urls

                                tweet_urls_all = []
                                tweet_original_urls_all = []
                                # Iterate over any URLs Tweet contains
                                if tweet_urls:
                                        directory_urls = directory_output + "/" + str(tweet.id) + "/urls/"
                                        if not os.path.exists(directory_urls):
                                                os.makedirs(directory_urls)
                                        for url in tweet_urls:
                                                try:
                                                        r = requests.get(url.expanded_url, timeout=10)
                                                        tweet_url_unique = url.url.split('/')[3]
                                                        file_url = str(directory_urls) + tweet_url_unique + ".html"
                                                        tweet_original_urls_all.append(url.expanded_url)
                                                        #tweet_original_urls_all.append(url.expanded_url.encode("utf-8"))
                                                        tweet_urls_all.append(file_url)
                                                        with open(file_url, "wb") as f:
                                                                f.write(r.content)
                                                except Exception as e:
                                                        print("Error: %s" % e)

                                                # Attempt to download github repo if it is a github.com link 
                                                if "github.com" in url.expanded_url:
                                                        try:
                                                                url_github_split = url.expanded_url.split('/')
                                                                url_github_download = url_github_split[0] + '//' + url_github_split[2] + '/' + url_github_split[3] + '/' + url_github_split[4] + '/archive/master.zip'
                                                                github_download = requests.get(url_github_download, timeout=30)
                                                                file_path_github = str(directory_urls) + url_github_split[4] + '.zip'
                                                                with open(file_path_github, "wb") as f:
                                                                        f.write(github_download.content)
                                                        except Exception as e:
                                                                print("Error: %s" % e)

                                # Really janky way to copy HTML into file for backup purposes
                                tweet_source = BeautifulSoup(tweet.source, "html.parser").a.string.encode("utf-8")
                                tweet_user = tweet.user.name.encode("utf-8")
                                tweet_screen_name = tweet.user.screen_name.encode("utf-8")
                                tweet_time = tweet.created_at.encode('utf-8')
                                tweets_complete.append(twitter_favorite(tweet_id, tweet_full_text, tweet_media_all, \
                                        tweet_original_media_all, tweet_urls_all, tweet_original_urls_all, tweet_source, \
                                        tweet_screen_name, tweet_user, tweet_time))
                                # For debugging
                                #if tweet_count > 5:
                                #        tweet_exists = False
                                #        break
                        else:

                                print("Tweet ID: %s\t\tTweet Count: %s\t\tStatus: Old" % (tweet.id, tweet_count))
                                tweet_id = tweet.id
                                tweet_count += 1



        except Exception as e:
                print("[!] Error: %s" % e)

# Save Tweets to tweet.index via Python pickeling (serialization)
with open(file_tweet_index,'wb') as f: 
        pickle.dump(tweets_complete,f)   


file_output_md = open(directory_output + "/_twitter_favorites.md", 'w')
file_output_md.write("# Twitter Favorites " + timestamp + " \n")
file_output_md.write("\n")
file_output_md.write("tweet_time | tweet_id | tweet\_full\_text | tweet\_media\_all | tweet\_urls\_all | tweet\_original\_urls | tweet_source | tweet_user | tweet\_screen\_name\n")
file_output_md.write("---------- | -------- | --------------- | --------------- | -------------- | ------------------- | ------------ | ---------- | -----------------\n")

# Sort list so oldest tweets are on the bottom
tweets_complete.sort(key=lambda x: x.id, reverse=True)

for i in tweets_complete:
        images = ''
        webpages = ''
        url_originals = ''

        try: 
                if i.media:
                        for image in i.media:
                                images += "[![" + image.split('/')[-1] + "](../" + image + ")](../" + image + ")<br /><br />"
                else:
                        images = ""
                if i.urls:
                        for webpage in i.urls:
                                webpages += "[" + webpage.split('/')[-1] + "](../" + webpage + ")<br />"
                else:
                        webpages = ""

                if i.urls_original:
                        for url_original in i.urls_original:
                                url_originals += "[" + str(url_original) + "](" + str(url_original) + ")<br />"
                        

                i.full_text = str(i.full_text).replace('\n', '<br /> ')

                file_output_md.write(str(i.time) + " | [" + str(i.id) + "](https://www.twitter.com/user/status/" + str(i.id) + ") | " + str(i.full_text) \
                        + " | " + str(images) + " | " + str(webpages) + " | " + str(url_originals) \
                        + " | " + str(i.source) + " | " + str(i.user) + " | " + str(i.screen_name) + "\n")
        
                file_output_md.flush()
                os.fsync(file_output_md)

        except Exception as e:
                print("Error: %s" % e)

file_output_md.close()



html_table_header = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
</head>
<body>
<div class="container table-responsive">
<h1>Twitter Favorites %s</h1>

<table class="table table-striped table-bordered">

<thead>
  <tr>
    <th>tweet_time</th>
    <th>tweet_id</th>
    <th>tweet_full_text</th>
    <th>tweet_media_all</th>
    <th>tweet_urls_all</th>
    <th>tweet_original_urls</th>
    <th>tweet_source</th>
    <th>tweet_user</th>
    <th>tweet_screen_name</th>
  </tr>
</thead>
<tbody>
""" % (timestamp)


html_table_footer = """
</tbody>
</table>
</div>
</body>
</html>
"""

file_output_html = open(directory_output + "/_twitter_favorites.html", 'w')
file_output_html.write(html_table_header)

for i in tweets_complete:
        images = ''
        webpages = ''
        url_originals = ''

        try: 
                if i.media:
                        for image in i.media:
                                images += '<img src="../' + image + '"<br /><br />'
                else:
                        images = ""
                if i.urls:
                        for webpage in i.urls:
                                webpages += '<a target="_blank" href="../' + webpage + '">' + webpage + '</a><br />'
                else:
                        webpages = ""

                if i.urls_original:
                        for url_original in i.urls_original:
                                url_originals += '<a target="_blank" href="' + str(url_original) + '">' + str(url_original) + '</a><br />'
                        

                i.full_text = str(i.full_text).replace('\n', '<br /> ')

                html_table_row = """
                <tr>
                        <td>%s</td>
                        <td><a href="https://www.twitter.com/user/status/%s">%s</a></td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                </tr>
                """ % (str(i.time, 'utf-8'), str(i.id), str(i.id), \
                str(i.full_text), str(images), str(webpages), str(url_originals), \
                str(i.source, 'utf-8'), str(i.user, 'utf-8'), str(i.screen_name, 'utf-8'))
        
                file_output_html.write(html_table_row)
                file_output_html.flush()
                os.fsync(file_output_html)
                

        except Exception as e:
                print("Error: %s" % e)

file_output_html.write(html_table_footer)
file_output_html.close()

print("[*] Completed download of Twitter Favorites")

