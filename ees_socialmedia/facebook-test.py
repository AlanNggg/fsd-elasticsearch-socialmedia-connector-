import os
import re
import facebook
import requests
from urllib.parse import quote
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def main():
    # Proxy configuration with URL encoded credentials
    username = 'km_search'
    password = '!kmsearch1234@'
    proxy_host = 'proxy3.hkfsd.hksarg:8080'
    
    proxies = {
        'http': f'http://{username}:{password}@{proxy_host}',
        'https': f'http://{username}:{password}@{proxy_host}'
    }

    os.environ['http_proxy'] =  'http://km_search:!kmsearch1234@@proxy3.hkfsd.hksarg:8080'
    os.environ['https_proxy'] = 'http://km_search:!kmsearch1234@@proxy3.hkfsd.hksarg:8080'

    # Initialize Facebook GraphAPI with proxies
    graph = facebook.GraphAPI(
        access_token='EAAEGMqCwAukBOZCYMP1UyZBMKRZAYxSBIrTOepOkGPNAr0dz80SR1daMKQEXB7SyJs1dpBsBbNVjtcLMHZBBsOtUhSBYJ3vNtv5PXVqOSZArVaU1WrAAd6CsdUl1FlSxLGJgIFjfoWxl2dFul5xwEcmAZC780WC0PeW8kRvLflp9o1UTOP88vt3eGgaGDvi59M',
        # proxies=proxies
    )
    
    profile = graph.get_object('me')
    print(profile['id'])

    posts = []
    posts_response = graph.get_connections(
        profile["id"], "posts", since='2018-01-01', until='2024-01-08', limit=100)

    while True:
        try:
            for post in posts_response["data"]:
                if 'message' not in post:
                    continue
                title = '香港消防處 Hong Kong Fire Services Department'

                message_list = re.split(r'\n\n|。', post['message'])
                if len(message_list) > 1:
                    title = message_list[0]

                posts.append(f"https://www.facebook.com/{post['id']}")

            # Use proxies for pagination requests
            posts_response = requests.get(
                posts_response["paging"]["next"], 
                proxies=proxies, 
                verify=False
            ).json()
        except KeyError as exception:
            print(exception)
            break
        except Exception as exception:
            print(exception)
            break

    print('posts: ', len(posts))

    posts2 = []
    posts_response = graph.get_connections(
        profile["id"], "posts", limit=100)

    while True:
        try:
            for post in posts_response["data"]:
                if 'message' not in post:
                    continue
                title = '香港消防處 Hong Kong Fire Services Department'

                message_list = re.split(r'\n\n|。', post['message'])
                if len(message_list) > 1:
                    title = message_list[0]

                posts2.append(f"https://www.facebook.com/{post['id']}")

            # Use proxies for pagination requests
            posts_response = requests.get(
                posts_response["paging"]["next"], 
                proxies=proxies, 
                verify=False
            ).json()
        except KeyError as exception:
            print(exception)
            break
        except Exception as exception:
            print(exception)
            break

    print('posts2: ', len(posts2))

    temp3 = []
    for element in posts2:
        if element not in posts:
            temp3.append(element)

    print(len(temp3))
    print(temp3)

if __name__ == "__main__":
    main()