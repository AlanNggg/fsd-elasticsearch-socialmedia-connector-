#
# Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
# or more contributor license agreements. Licensed under the Elastic License 2.0;
# you may not use this file except in compliance with the Elastic License 2.0.
#
"""This module allows to run a full sync against a Network Drives.

    It will attempt to sync absolutely all documents that are available in the
    third-party system and ingest them into Enterprise Search instance.
"""
from datetime import datetime

from .base_command import BaseCommand
from .checkpointing import Checkpoint
from .connector_queue import ConnectorQueue
from .local_storage import LocalStorage
from .sync_elastic_search import SyncElasticSearch
from .sync_enterprise_search import SyncEnterpriseSearch
from .sync_socialmedia import SyncSocialMedia
from .utils import get_current_time, split_date_range_into_chunks

INDEXING_TYPE = "full"


class FullSyncCommand(BaseCommand):
    """This class start executions of fullsync feature."""

    def start_producer(self, queue):
        """This method starts async calls for the producer which is responsible
        for fetching documents from the Network Drive and pushing them in the shared queue
        :param queue: Shared queue to store the fetched documents
        """
        self.logger.debug("Starting the full indexing..")

        current_time = (datetime.utcnow()).strftime("%Y-%m-%dT%H:%M:%SZ")

        # thread_count = self.config.get_value("socialmedia_sync_thread_count")
        thread_count = 1

        start_time, end_time = self.config.get_value(
            "start_time"), current_time

        try:
            sync_socialmedia = SyncSocialMedia(
                self.config,
                self.logger,
                self.youtube_client,
                self.facebook_client,
                self.indexing_rules,
                queue,
                start_time,
                end_time
            )
            datelist = split_date_range_into_chunks(
                start_time,
                end_time,
                thread_count,
            )
            for collection in self.config.get_value("socialmedia.collections"):
                storage_with_collection = self.local_storage.get_storage_with_collection()
                storage_with_collection["global_keys"][collection] = sync_socialmedia.perform_sync(
                    self.producer, datelist, thread_count, collection)

            # enterprise_search_sync_thread_count = self.config.get_value("enterprise_search_sync_thread_count")
            enterprise_search_sync_thread_count = 1
            for _ in range(enterprise_search_sync_thread_count):
                queue.end_signal()
        except Exception as exception:
            self.logger.error(
                f"Error while Fetching from the Social Media. Error: {exception}. Checkpoint not saved")
            raise exception

        self.local_storage.update_storage(storage_with_collection)

    def start_consumer(self, queue):
        """This method starts async calls for the consumer which is responsible for indexing documents to the Enterprise Search
        :param queue: Shared queue to fetch the stored documents
        """
        # thread_count = self.config.get_value(
        #     "enterprise_search_sync_thread_count")
        thread_count = 1
        sync_es = SyncElasticSearch(
            self.config, self.logger, self.elastic_search_custom_client, queue)

        self.consumer(thread_count, sync_es.perform_sync)

        results = sync_es.get_status()

        return results

    def execute(self):
        """This function execute the full sync."""
        config = self.config
        logger = self.logger
        current_time = get_current_time()
        checkpoint = Checkpoint(config, logger)

        logger.info(f"Indexing started at: {current_time}")

        queue = ConnectorQueue(logger)
        self.start_producer(queue)
        total_documents_found, total_documents_indexed, total_documents_appended, total_documents_updated, total_documents_failed = self.start_consumer(
            queue)
        checkpoint.set_checkpoint(current_time, INDEXING_TYPE, 'socialmedia')
        logger.info(f"Indexing ended at: {get_current_time()}")

        output = {
            'total_documents_found': total_documents_found,
            'total_documents_indexed': total_documents_indexed,
            'total_documents_appended': total_documents_appended,
            'total_documents_updated': total_documents_updated,
            'total_documents_failed': total_documents_failed
        }

        return output
