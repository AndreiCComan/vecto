"""Tests for embeddings module."""

import unittest
from vecto.benchmarks.similarity import Similarity
from vecto.benchmarks.analogy import *
from vecto.benchmarks.text_classification import Text_classification
from vecto.embeddings import load_from_dir


path_similarity_dataset = "./tests/data/benchmarks/similarity/"
path_analogy_dataset = "./tests/data/benchmarks/analogy/"
path_text_classification_dataset = "./tests/data/benchmarks/text_classification/"

class Tests(unittest.TestCase):


    def test_similarity(self):
        embs = load_from_dir("tests/data/embeddings/text/plain_with_file_header")
        similarity = Similarity()
        result = similarity.get_result(embs, path_similarity_dataset)
        print(result)

        similarity = Similarity(ignore_oov=False)
        result = similarity.get_result(embs, path_similarity_dataset)
        print(result)

    def test_analogy(self):
        embs = load_from_dir("./tests/data/embeddings/text/plain_with_file_header")

        analogy = LinearOffset()
        result = analogy.get_result(embs, path_analogy_dataset)
        print(result)
        analogy = PairDistance()
        result = analogy.get_result(embs, path_analogy_dataset)
        print(result)
        analogy = ThreeCosMul()
        result = analogy.get_result(embs, path_analogy_dataset)
        print(result)
        analogy = ThreeCosMul2()
        result = analogy.get_result(embs, path_analogy_dataset)
        print(result)
        # analogy = SimilarToAny()
        # result = analogy.get_result(embs, path_analogy_dataset)
        # print(result)
        # analogy = SimilarToB()
        # result = analogy.get_result(embs, path_analogy_dataset)
        # print(result)
        analogy = LRCos()
        result = analogy.get_result(embs, path_analogy_dataset)
        print(result)

        # big embs and dataset test
        # embs = load_from_dir("/home/bofang/Documents/embeddings/negative_sampling/fair/")
        # result = analogy.get_result(embs, "/home/bofang/Downloads/BATS_3.0_small")
        # print(result)

    def test_text_classification(self):
        embs = load_from_dir("./tests/data/embeddings/text/plain_with_file_header")
        tc = Text_classification()
        result = tc.get_result(embs, path_text_classification_dataset)
        print(result)



# Tests().test_text_classification()