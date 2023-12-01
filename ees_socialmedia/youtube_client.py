import googleapiclient.discovery
import googleapiclient.errors


class Youtube:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config
        self.api_service_name = "youtube"
        self.api_version = self.config.get_value("youtube.api_version")
        self.api_key = self.config.get_value("youtube.api_key")
        self.channel_id = self.config.get_value("youtube.channel_id")

        self.youtube = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, developerKey=self.api_key)
        

    def fetch_videos(self, start_time = None, end_time = None):
        channel_response = self.youtube.channels().list(
            part='contentDetails',
            id=self.channel_id,
        ).execute()

        channel = channel_response.get('items')[0]
        upload_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']

        request = self.youtube.playlistItems().list(
            part="snippet,contentDetails,id,status",
            playlistId=upload_playlist_id,
            maxResults=50
        )

        videos = []
        while request:
            playlist_item_response = request.execute()

            for playlist_item in playlist_item_response.get("items", []):
                video_id = playlist_item['snippet']['resourceId']['videoId']
                videos.append({
                    'id': video_id,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'title': playlist_item['snippet']['title'],
                    'body': playlist_item['snippet']['description'],
                    'date': playlist_item['snippet']['publishedAt'],
                    'thumbnails': playlist_item['snippet']['thumbnails']['high']['url'],
                    'source': 'socialmedia',
                    'category': ['youtube'],
                    'type': 'youtube'
                })        
            

            request = self.youtube.playlistItems().list_next(request, playlist_item_response)

        return videos

    def search(self, start_time = None, end_time = None):
        request = self.youtube.search().list(
            part='id',
            channelId=self.channel_id,
            maxResults=50,
            type='video'
        )

        videos = []
        video_ids = []
        while request is not None:
            search_response = request.execute()

            for search_result in search_response.get('items', []):
                video_ids.append(search_result['id']['videoId'])

            request = self.youtube.search().list_next(request, search_response)

        video_ids = ",".join(video_ids)

        video_response = self.youtube.videos().list(
            id=video_ids,
            part='id,snippet'
        ).execute()

        for video_result in video_response.get("items", []):
            videos.append({
                'id': video_result['id'],
                'url': f"https://www.youtube.com/watch?v={video_result['id']}",
                'title': video_result['snippet']['title'],
                'body': video_result['snippet']['description'],
                'date': video_result['snippet']['publishedAt'],
                'thumbnails': video_result['snippet']['thumbnails']['high']['url'],
                'source': 'socialmedia',
                'category': ['link', 'youtube'],
                'type': 'youtube'
            })

        return videos
