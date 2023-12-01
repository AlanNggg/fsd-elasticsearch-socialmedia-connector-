from .constant import FACEBOOK, YOUTUBE


class SyncSocialMedia:

    def __init__(
        self,
        config,
        logger,
        youtube_client,
        facebook_client,
        indexing_rules,
        documents_to_index,
        start_time = None,
        end_time = None,
    ):
        self.logger = logger
        self.config = config
        self.youtube_client = youtube_client
        self.facebook_client = facebook_client
        self.indexing_rules = indexing_rules
        self.documents_to_index = documents_to_index
        # for incremental sync
        self.start_time = start_time
        self.end_time = end_time

    def perform_sync(self, collection):
        self.logger.info(f"fetching data from {collection}")
        ids_storage = {}

        fetched_documents = []
        try:
            if collection == YOUTUBE:
                fetched_documents += self.youtube_client.fetch_videos(self.start_time, self.end_time)

            if collection == FACEBOOK:
                fetched_documents += self.facebook_client.fetch_posts(self.start_time, self.end_time)

            self.documents_to_index.extend(fetched_documents)
        except Exception as exception:
            self.logger.error(f"Error while fetching videos. Error: {exception}")

        for doc in fetched_documents:
            ids_storage.update({doc["id"]: doc["url"]})

        return ids_storage
        