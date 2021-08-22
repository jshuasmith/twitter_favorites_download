# Twitter Favorites Download

This script uses the Twitter API to download and save your Twitter Favorites (aka, Likes) to an HTML and MarkDown page that allows for easy offline searching and keeps a copy in case the original tweet or destination content is deleted. Copies of the media (ie, images) as well as a copy of the webpage linked to, if any, are saved locally. Tweets are indexed and saved to avoid having to pull same data repetitively so you can easily set this up as a cron job.

## Usage Instructions:

1. **Get your Twitter API keys:**  
- Log into your Twitter account.  
- Go to https://dev.twitter.com/apps  
- Create an app (must be a globally unique name)  
- Change permissions if necessary (depending if you want to just read,write or execute)  
- Go To API keys section and click generate ACCESS TOKEN.  

Now you should have these tokens:

'oauth_access_token' => Access token  
'oauth_access_token_secret' => Access token secret  
'consumer_key' => API key  
'consumer_secret' => API secret  

2. Add these keys to the config.file (no quotes around the values in the config.file)  
3. Run ```sudo pip install -r requirements.txt``` (if you aren't using virtualenv you might have to run this with sudo rights)  
4. Run ```python twitter_favorites_download.py ```  

Once the script is complete look in the destination_folder_name for your HTML and MarkDown files. If you want to use MarkDown you will need a viewer for your browser or standalone for your OS (MacDown for macOS isn't bad).

This script has been tested on Ubuntu 16.04 only.   

(c) Joshua Smith - Cornerstone Security  
https://www.cornerstonesec.com
