import os
import pickle
import urllib.parse as p
import re

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def youtube_authenticator():
    '''
        Establish connection to Youtube
    '''
    scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']
    credentials = None
    if os.path.exists('token.pickle'):
        print('Loading credentials from file')
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    if not credentials or credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes)
            credentials = flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return build('youtube', 'v3', credentials=credentials)

def get_video_id_by_url(url):
    '''
        Return the Video ID from the video `url`
    '''
    parsed_url = p.urlparse(url)
    video_id = p.parse_qs(parsed_url.query).get('v')
    if video_id:
        return video_id[0]
    else:
        raise Exception(f'Wasnt able to parse video URL: {url}')

def get_video_details(youtube, **kwargs):
    '''
        Get Video Details
    '''
    return youtube.videos().list(
        part='snippet,contentDetails,statistics',
        **kwargs
    ).execute()

def print_video_infos(video_response):
    '''
        Print Video information
    '''
    items = video_response.get('items')[0]
    snippet = items['snippet']
    statistics = items['statistics']
    content_details = items['contentDetails']
    channel_title = snippet['channelTitle']
    title = snippet['title']
    description = snippet['description']
    publish_time = snippet['publishedAt']
    comment_count = statistics['commentCount']
    like_count = statistics['likeCount']
    dislike_count = statistics['dislikeCount']
    view_count = statistics['viewCount']
    duration = content_details['duration']
    print(duration)
    parsed_duration = list(filter(None, re.split(r'[A-Z]+' , duration)))
    duration_str = ':'.join(parsed_duration)
    print(f'''\
        Title: {title}
        Description: {description}
        Channel Title: {channel_title}
        Publish time: {publish_time}
        Duration: {duration_str}
        Number of comments: {comment_count}
        Number of likes: {like_count}
        Number of dislikes: {dislike_count}
        Number of views: {view_count}
    ''')

def main():
    youtube = youtube_authenticator()
    video_url = input('Enter the url of the youtube video you want to get details for: ')
    video_id = get_video_id_by_url(video_url)
    response = get_video_details(youtube, id=video_id)
    print_video_infos(response)

if __name__ == '__main__':
	main()



