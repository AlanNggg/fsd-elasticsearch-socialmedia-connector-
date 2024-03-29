#
# Copyright Elasticsearch B.V. and/or licensed to Elasticsearch B.V. under one
# or more contributor license agreements. Licensed under the Elastic License 2.0;
# you may not use this file except in compliance with the Elastic License 2.0.
#
"""This module allows to run an incremental sync against a Sharepoint Server instance.

It will attempt to sync documents that have changed or have been added in the
third-party system recently and ingest them into Enterprise Search instance.

Recency is determined by the time when the last successful incremental or full job
was ran."""
from datetime import datetime

from .base_command import BaseCommand
from .checkpointing import Checkpoint
from .connector_queue import ConnectorQueue
from .sync_elastic_search import SyncElasticSearch
from .sync_enterprise_search import SyncEnterpriseSearch
from .sync_socialmedia import SyncSocialMedia
from .utils import get_current_time, split_date_range_into_chunks

INDEXING_TYPE = "incremental"


class IncrementalSyncCommand(BaseCommand):
    """This class start execution of incremental sync feature."""

    def start_producer(self, queue, time_range):
        """This method starts async calls for the producer which is responsible for fetching documents from the
        SharePoint and pushing them in the shared queue
        :param queue: Shared queue to fetch the stored documents
        """
        self.logger.debug("Starting the incremental indexing..")

        # thread_count = self.config.get_value("socialmedia_sync_thread_count")
        thread_count = 1

        start_time, end_time = time_range["start_time"], time_range["end_time"]

        try:
            sync_socialmedia = SyncSocialMedia(
                self.config,
                self.logger,
                self.youtube_client,
                self.facebook_client,
                self.indexing_rules,
                queue,
                start_time,
                end_time,
            )
            datelist = split_date_range_into_chunks(
                start_time,
                end_time,
                thread_count,
            )
            for collection in self.config.get_value("socialmedia.collections"):
                storage_with_collection = self.local_storage.get_storage_with_collection()

                try:
                    storage_with_collection["global_keys"][collection] = sync_socialmedia.perform_sync(
                        self.producer, datelist, thread_count, collection)
                except ValueError as value_error:
                    self.logger.error(
                        f"Exception while updating storage: {value_error}")

            # enterprise_search_sync_thread_count = self.config.get_value("enterprise_search_sync_thread_count")
            enterprise_search_sync_thread_count = 1
            for _ in range(enterprise_search_sync_thread_count):
                queue.end_signal()
        except Exception as exception:
            self.logger.exception(
                f"Error while fetching the objects . Error {exception}")
            raise exception
        self.local_storage.update_storage(storage_with_collection)

    def start_consumer(self, queue):
        """This method starts async calls for the consumer which is responsible for indexing documents to the
        Enterprise Search
        :param queue: Shared queue to fetch the stored documents
        """
        # thread_count = self.config.get_value(
        #     "enterprise_search_sync_thread_count")
        thread_count = 1
        sync_es = SyncElasticSearch(
            self.config, self.logger, self.elastic_search_custom_client, queue)
        self.consumer(thread_count, sync_es.perform_sync, (True,))

        results = sync_es.get_status()

        return results

    def execute(self):
        """This function execute the start function."""
        config = self.config
        logger = self.logger
        current_time = get_current_time()

        checkpoint = Checkpoint(config, logger)

        start_time, end_time = checkpoint.get_checkpoint(
            current_time, 'socialmedia')

        time_range = {
            "start_time": start_time,
            "end_time": end_time,
        }
        logger.info(f"Indexing started at: {current_time}")

        queue = ConnectorQueue(logger)
        self.start_producer(queue, time_range)
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
