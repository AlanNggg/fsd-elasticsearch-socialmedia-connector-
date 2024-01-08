import threading

from .constant import FACEBOOK, YOUTUBE


class SyncSocialMedia:

    def __init__(
        self,
        config,
        logger,
        youtube_client,
        facebook_client,
        indexing_rules,
        queue,
        start_time=None,
        end_time=None,
    ):
        self.logger = logger
        self.config = config
        self.youtube_client = youtube_client
        self.facebook_client = facebook_client
        self.indexing_rules = indexing_rules
        self.queue = queue
        # for incremental sync
        self.start_time = start_time
        self.end_time = end_time

    def fetch_and_append_videos_to_queue(self, duration):
        documents = self.youtube_client.fetch_videos()

        if documents:
            self.logger.debug(
                f"Thread ID {threading.get_ident()} find {len(documents.get('data'))} drive items"
            )
            self.queue.put(documents)
            self.logger.debug(
                f"Thread ID {threading.get_ident()} added list of {len(documents.get('data'))} drive items into the queue"
            )
            return documents

    def fetch_and_append_posts_to_queue(self, duration):
        start_time, end_time = duration[0], duration[1]
        documents = self.facebook_client.fetch_posts(start_time, end_time)

        if documents:
            self.logger.debug(
                f"Thread ID {threading.get_ident()} find {len(documents.get('data'))} drive items"
            )
            self.queue.put(documents)
            self.logger.debug(
                f"Thread ID {threading.get_ident()} added list of {len(documents.get('data'))} drive items into the queue"
            )
            return documents

    def perform_sync(self, producer, date_ranges, thread_count, collection):
        self.logger.info(f"fetching data from {collection}")

        ids_storage = {}

        fetched_documents = []
        try:
            if collection == YOUTUBE:
                time_range_list = [(date_ranges[0], date_ranges[-1])]
                fetched_documents += producer(
                    thread_count, self.fetch_and_append_videos_to_queue, [], time_range_list, wait=True)

            if collection == FACEBOOK:
                time_range_list = [(date_ranges[num], date_ranges[num + 1])
                                   for num in range(0, thread_count)]
                fetched_documents += producer(
                    thread_count, self.fetch_and_append_posts_to_queue, [], time_range_list, wait=True)

        except Exception as exception:
            self.logger.error(
                f"Error while fetching videos. Error: {exception}")

        for docs in fetched_documents:
            for doc in docs:
                ids_storage.update({doc["id"]: doc["url"]})

        return ids_storage
