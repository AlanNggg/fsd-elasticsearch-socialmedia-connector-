import re
from datetime import datetime

import facebook
import requests


class Facebook:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config
        self.access_token = self.config.get_value("facebook.access_token")
        self.graph = facebook.GraphAPI(self.access_token)
        self.profile = self.graph.get_object('me')

    def fetch_posts(self, start_time, end_time):
        posts = []

        posts_response = self.graph.get_connections(self.profile["id"], "posts")

        while True:
            try:
                for post in posts_response["data"]:
                    if 'message' not in post:
                        continue
                    title = '香港消防處 Hong Kong Fire Services Department'

                    # extract title from message
                    message_list = re.split(r'\n\n|。', post['message'])
                    if len(message_list) > 1:
                        title = message_list[0]
        
                    posts.append({
                        'id': post['id'],
                        'url': f"https://www.facebook.com/{post['id']}",
                        'title': title,
                        'body': post['message'],
                        'date': post['created_time'],
                        'source': 'socialmedia',
                        'category': ['post', 'facebook'],
                        'type': 'facebook'
                    })

                # Attempt to make a request to the next page of data, if it exists.
                posts_response = requests.get(posts_response["paging"]["next"]).json()
            except KeyError as exception:
                break

        return posts