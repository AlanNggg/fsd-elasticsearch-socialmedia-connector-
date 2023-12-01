import re

import facebook
import requests


def main():
    graph = facebook.GraphAPI('EAAEGMqCwAukBOZCYMP1UyZBMKRZAYxSBIrTOepOkGPNAr0dz80SR1daMKQEXB7SyJs1dpBsBbNVjtcLMHZBBsOtUhSBYJ3vNtv5PXVqOSZArVaU1WrAAd6CsdUl1FlSxLGJgIFjfoWxl2dFul5xwEcmAZC780WC0PeW8kRvLflp9o1UTOP88vt3eGgaGDvi59M')
    profile = graph.get_object('me')

    posts = []

    posts_response = graph.get_connections(profile["id"], "posts")

    while True:
        try:
            for post in posts_response["data"]:
                if 'message' not in post:
                    continue
                title = '香港消防處 Hong Kong Fsire Services Department'

                # extract title from message
                message_list = re.split(r'\n\n|。', post['message'])
                if len(message_list) > 1:
                    title = message_list[0]
    
                print(len(message_list), title)
                
                posts.append({
                    'id': post['id'],
                    'url': f"https://www.facebook.com/{post['id']}",
                    'title': title,
                    'body': post['message'],
                    'date': post['created_time'],
                    'source': 'socialmedia',
                    'category': ['link', 'facebook'],
                    'type': 'facebook'
                })

            # Attempt to make a request to the next page of data, if it exists.
            posts_response = requests.get(posts_response["paging"]["next"]).json()
        except KeyError as exception:
            print(exception)
            break
        except Exception as exception:
            print(exception)
            break

    print('posts: ', len(posts))

if __name__ == "__main__":
    main()