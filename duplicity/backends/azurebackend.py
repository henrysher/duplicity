# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2013 Matthieu Huin <mhu@enovance.com>
# Copyright 2015 Scott McKenzie <noizyland@gmail.com>
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# Duplicity is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with duplicity; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os

import duplicity.backend
from duplicity import globals
from duplicity import log
from duplicity.errors import BackendException


class AzureBackend(duplicity.backend.Backend):
    """
    Backend for Azure Blob Storage Service
    """
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        # Import Microsoft Azure Storage SDK for Python library.
        try:
            import azure
            import azure.storage
            if hasattr(azure.storage, 'BlobService'):
                # v0.11.1 and below
                from azure.storage import BlobService
                self.AzureMissingResourceError = azure.WindowsAzureMissingResourceError
                self.AzureConflictError = azure.WindowsAzureConflictError
            else:
                # v1.0.0 and above
                import azure.storage.blob
                if hasattr(azure.storage.blob, 'BlobService'):
                    from azure.storage.blob import BlobService
                else:
                    from azure.storage.blob.blockblobservice import BlockBlobService as BlobService
                self.AzureMissingResourceError = azure.common.AzureMissingResourceHttpError
                self.AzureConflictError = azure.common.AzureConflictHttpError
        except ImportError as e:
            raise BackendException("""\
Azure backend requires Microsoft Azure Storage SDK for Python (https://pypi.python.org/pypi/azure-storage/).
Exception: %s""" % str(e))

        # TODO: validate container name
        self.container = parsed_url.path.lstrip('/')
        
        if globals.azure_region == 'global':
            suffix = "core.windows.net"
        elif globals.azure_region == 'germany':
            suffix = "core.cloudapi.de"
        elif globals.azure_region == 'china':
            suffix = "core.chinacloudapi.cn"

        if 'AZURE_ACCOUNT_NAME' not in os.environ:
            raise BackendException('AZURE_ACCOUNT_NAME environment variable not set.')

        if 'AZURE_ACCOUNT_KEY' in os.environ:
            self.blob_service = BlobService(account_name=os.environ['AZURE_ACCOUNT_NAME'],
                                            account_key=os.environ['AZURE_ACCOUNT_KEY'],
                                            endpoint_suffix=suffix)
            self._create_container()
        elif 'AZURE_SHARED_ACCESS_SIGNATURE' in os.environ:
            self.blob_service = BlobService(account_name=os.environ['AZURE_ACCOUNT_NAME'],
                                            sas_token=os.environ['AZURE_SHARED_ACCESS_SIGNATURE'],
                                            endpoint_suffix=suffix)
        else:
            raise BackendException(
                'Neither AZURE_ACCOUNT_KEY nor AZURE_SHARED_ACCESS_SIGNATURE environment variable not set.')

        if globals.azure_max_single_put_size:
            # check if we use azure-storage>=0.30.0
            try:
                _ = self.blob_service.MAX_SINGLE_PUT_SIZE
                self.blob_service.MAX_SINGLE_PUT_SIZE = globals.azure_max_single_put_size
            # fallback for azure-storage<0.30.0
            except AttributeError:
                self.blob_service._BLOB_MAX_DATA_SIZE = globals.azure_max_single_put_size

        if globals.azure_max_block_size:
            # check if we use azure-storage>=0.30.0
            try:
                _ = self.blob_service.MAX_BLOCK_SIZE
                self.blob_service.MAX_BLOCK_SIZE = globals.azure_max_block_size
            # fallback for azure-storage<0.30.0
            except AttributeError:
                self.blob_service._BLOB_MAX_CHUNK_DATA_SIZE = globals.azure_max_block_size

    def _create_container(self):
        try:
            self.blob_service.create_container(self.container, fail_on_exist=True)
        except self.AzureConflictError:
            # Indicates that the resource could not be created because it already exists.
            pass
        except Exception as e:
            log.FatalError("Could not create Azure container: %s"
                           % unicode(e.message).split('\n', 1)[0],
                           log.ErrorCode.connection_failed)

    def _put(self, source_path, remote_filename):
        kwargs = {}
        if globals.azure_max_connections:
            kwargs['max_connections'] = globals.azure_max_connections

        # https://azure.microsoft.com/en-us/documentation/articles/storage-python-how-to-use-blob-storage/#upload-a-blob-into-a-container
        try:
            self.blob_service.create_blob_from_path(self.container, remote_filename, source_path.name, **kwargs)
        except AttributeError:  # Old versions use a different method name
            self.blob_service.put_block_blob_from_path(self.container, remote_filename, source_path.name, **kwargs)

    def _get(self, remote_filename, local_path):
        # https://azure.microsoft.com/en-us/documentation/articles/storage-python-how-to-use-blob-storage/#download-blobs
        self.blob_service.get_blob_to_path(self.container, remote_filename, local_path.name)

    def _list(self):
        # https://azure.microsoft.com/en-us/documentation/articles/storage-python-how-to-use-blob-storage/#list-the-blobs-in-a-container
        blobs = []
        marker = None
        while True:
            batch = self.blob_service.list_blobs(self.container, marker=marker)
            blobs.extend(batch)
            if not batch.next_marker:
                break
            marker = batch.next_marker
        return [blob.name for blob in blobs]

    def _delete(self, filename):
        # http://azure.microsoft.com/en-us/documentation/articles/storage-python-how-to-use-blob-storage/#delete-blobs
        self.blob_service.delete_blob(self.container, filename)

    def _query(self, filename):
        prop = self.blob_service.get_blob_properties(self.container, filename)
        try:
            info = {'size': int(prop.properties.content_length)}
        except AttributeError:
            # old versions directly returned the properties
            info = {'size': int(prop['content-length'])}
        return info

    def _error_code(self, operation, e):
        if isinstance(e, self.AzureMissingResourceError):
            return log.ErrorCode.backend_not_found


duplicity.backend.register_backend('azure', AzureBackend)
