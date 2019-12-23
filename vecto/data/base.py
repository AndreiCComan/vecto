import fnmatch
import os
import tarfile
import logging
import tempfile

from vecto.utils.metadata import WithMetaData
from .io import fetch_file

logger = logging.getLogger(__name__)
# TODO: get dataset dir from config
dir_datasets = "/home/blackbird/.vecto/datasets"

class Dataset(WithMetaData):
    """
    Container class for stock datasets.
    Arguments:
        path (str): local path to place files
    """

    def __init__(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError("test dataset dir does not exist:" + path)
        super().__init__(path)
        self.path = path

    def file_iterator(self):
        for root, _, filenames in os.walk(self.path):
            for filename in fnmatch.filter(sorted(filenames), '*'):
                if filename.endswith('json'):
                    continue
                yield(os.path.join(root, filename))


def download_index():
    logger.info("downloading index of resources")
    dir_temp = os.path.join(tempfile.gettempdir(), "vecto", "tmp")
    os.makedirs(dir_temp, exist_ok=True)
    path_tar = os.path.join(dir_temp, "resources.tar")
    url_resources = "https://github.com/vecto-ai/vecto-resources/tarball/master/"
    fetch_file(url_resources, path_tar)
    with tarfile.open(path_tar) as tar:
        for member in tar.getmembers():
            parts = member.name.split("/")
            if len(parts) <= 1: 
                continue
            if parts[1] != "resources":
                continue
            member.path = os.path.join(*parts[1:])
            tar.extract(member, dir_datasets)


def gen_metadata_snippets(path):
    for name in os.listdir(path):
        if name == "metadata.json":
            yield os.path.join(path, name)
        else:
            sub = os.path.join(path, name)
            if os.path.isdir(sub):
                yield from gen_metadata_snippets(sub)

def load_dataset_infos():
    for f_meta in gen_metadata_snippets(dir_datasets):
        print(f_meta)


def get_dataset(name):
    load_dataset_infos()
    path_dataset = os.path.join(dir_datasets, name)
    dataset = Dataset(path_dataset)
    return dataset
    # TODO: check if it seats locally
    # TODO: download
