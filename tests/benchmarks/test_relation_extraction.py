"""Tests for analogy benchmark."""

import contextlib
import unittest
import io
from os import path
from vecto.benchmarks.relation_extraction import *
from vecto.benchmarks import visualize
from vecto.embeddings import load_from_dir
from tests.test_setup import run_module

path_similarity_dataset = path.join('.', 'tests', 'data', 'benchmarks', 'relation_extraction')
path_emb = path.join('tests', 'data', 'embeddings', 'text', 'plain_with_file_header')


class Tests(unittest.TestCase):

    def test_api(self):
        # embs = load_from_dir(path_emb)
        # relation_extraction = Relation_extraction()
        # result = relation_extraction.get_result(embs, path_similarity_dataset)
        # self.assertIsInstance(result, dict)
        # print(result)
        pass

    def test_cli(self):
        # sio = io.StringIO()
        # with contextlib.redirect_stdout(sio):
        #     run_module("vecto.benchmarks.relation_extraction",
        #                path_emb,
        #                path_similarity_dataset,
        #                "--path_out", "/tmp/vecto/benchmarks/")
        #
        # with self.assertRaises(FileNotFoundError):
        #     sio = io.StringIO()
        #     with contextlib.redirect_stdout(sio):
        #         run_module("vecto.benchmarks.similarity",
        #                    path_emb + "NONEXISTING",
        #                    path_similarity_dataset,
        #                    "--path_out", "/tmp/vecto/benchmarks/")
        #
        # from matplotlib import pyplot as plt
        # visualize.plot_accuracy("/tmp/vecto/benchmarks/relation_extraction", key_secondary="experiment_setup.dataset")
        # plt.savefig("/tmp/vecto/benchmarks/relation_extraction.pdf", bbox_inches="tight")
        pass

# Tests().test_cli()
