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
        document_list = self.youtube_client.fetch_videos()
        documents = {"type": YOUTUBE, "data": document_list}

        if documents:
            self.logger.info(
                f"Thread ID {threading.get_ident()} find {len(documents.get('data'))} drive items"
            )
            self.queue.put(documents)
            self.logger.info(
                f"Thread ID {threading.get_ident()} added list of {len(documents.get('data'))} drive items into the queue"
            )
            return document_list

    def fetch_and_append_posts_to_queue(self, duration):
        start_time, end_time = duration[0], duration[1]
        document_list = self.facebook_client.fetch_posts(start_time, end_time)
        documents = {"type": FACEBOOK, "data": document_list}

        if documents:
            self.logger.info(
                f"Thread ID {threading.get_ident()} find {len(documents.get('data'))} posts from {start_time} to {end_time}"
            )
            self.queue.put(documents)
            self.logger.info(
                f"Thread ID {threading.get_ident()} added list of {len(documents.get('data'))} posts into the queue"
            )
            return document_list

    def perform_sync(self, producer, date_ranges, thread_count, collection):
        self.logger.info(f"fetching data from {collection}")

        ids_storage = {}

        fetched_documents = []
        try:
            if collection == YOUTUBE:
                time_range_list = [(date_ranges[0], date_ranges[-1])]
                fetched_documents += producer(
                    1, self.fetch_and_append_videos_to_queue, [], time_range_list, wait=True)

            if collection == FACEBOOK:
                time_range_list = [(date_ranges[num], date_ranges[num + 1])
                                   for num in range(0, thread_count)]
                # facebook query since=start_time, until=end_time has bug, cannot do multithread
                fetched_documents += producer(
                    1, self.fetch_and_append_posts_to_queue, [], time_range_list, wait=True)

        except Exception as exception:
            self.logger.error(
                f"Error while fetching social media. Error: {exception}")

        for docs in fetched_documents:
            for doc in docs:
                ids_storage.update({doc["id"]: doc["url"]})

        return ids_storage
