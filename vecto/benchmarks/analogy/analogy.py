import datetime
import os
import scipy
import uuid
import numpy as np
import logging
import progressbar
# from tqdm import tqdm
import sklearn
from itertools import product
from vecto.data import Dataset
from ..base import Benchmark
from .io import get_pairs
from .solvers import *

logger = logging.getLogger(__name__)


def select_method(key):
    if key == "3CosAvg":
        method = ThreeCosAvg
    #elif key == "SimilarToAny":
    #    method = SimilarToAny(options)
    #elif key == "SimilarToB":
    #    method = SimilarToB(options)
    elif key == "3CosMul":
        method = ThreeCosMul
    elif key == "3CosAdd":
        method = LinearOffset
    #elif key == "PairDistance":
    #    method = PairDistance(options)
    elif key == "LRCos" or key == "SVMCos":
        method = LRCos
    else:
        raise RuntimeError("method name not recognized")
    return method


class Analogy(Benchmark):

    def __init__(self,
                 method="3CosAdd",
                 normalize=True,
                 ignore_oov=True,
                 do_top5=True,
                 # need_subsample=False,
                 size_cv_test=1,
                 set_aprimes_test=None,
                 exclude=True,
                 name_classifier='LR',
                 name_kernel="linear"):
        self.normalize = normalize
        self.method = method
        self.ignore_oov = ignore_oov
        self.do_top5 = do_top5
        # self.need_subsample = need_subsample
        self.normalize = normalize
        self.size_cv_test = size_cv_test
        self.set_aprimes_test = set_aprimes_test
#        self.inverse_regularization_strength = inverse_regularization_strength
        self.exclude = exclude
        self.name_classifier = name_classifier
        self.name_kernel = name_kernel

        self.stats = {}


        # this are some hard-coded bits which will be implemented later
        self.result_miss = {
            "rank": -1,
            "reason": "missing words"
        }


    # def is_at_least_one_word_present(self, words):
    #     for w in words:
    #         if self.embs.vocabulary.get_id(w) >= 0:
    #             return True
    #     return False


    # def gen_vec_single_nonoise(self, pairs):
    #     a, a_prime = zip(*pairs)
    #     a_prime = [i for sublist in a_prime for i in sublist]
    #     a_prime = [i for i in a_prime if self.embs.vocabulary.get_id(i) >= 0]
    #     x = list(a_prime) + list(a)
    #     X = np.array([self.embs.get_vector(i) for i in x])
    #     Y = np.hstack([np.ones(len(a_prime)), np.zeros(len(x) - len(a_prime))])
    #     return X, Y

    def get_crowndedness(self, vector):
        scores = self.get_most_similar_fast(vector)
        scores.sort()
        return (scores[-11:-1][::-1]).tolist()

    # def create_list_test_right(self, pairs):
    #     global set_aprimes_test
    #     a, a_prime = zip(*pairs)
    #     a_prime = [i for sublist in a_prime for i in sublist]
    #     set_aprimes_test = set(a_prime)

    # def get_distance_closest_words(self, center, cnt_words=1):
    #     scores = self.get_most_similar_fast(center)
    #     ids_max = np.argsort(scores)[::-1]
    #     distances = np.zeros(cnt_words)
    #     for i in range(cnt_words):
    #         distances[i] = scores[ids_max[i + 1]]
    #     return distances.mean()

    def get_rank(self, source, center):
        if isinstance(center, str):
            center = self.embs.get_vector(center)
        if isinstance(source, str):
            source = [source]
        scores = self.get_most_similar_fast(center)
        ids_max = np.argsort(scores)[::-1]
        for i in range(ids_max.shape[0]):
            if self.embs.vocabulary.get_word_by_id(ids_max[i]) in source:
                break
        rank = i
        return rank

    def run_category(self, pairs):
        self.cnt_total_correct = 0
        self.cnt_total_total = 0
        details = []
        kfold = sklearn.model_selection.KFold(n_splits=len(pairs) // self.size_cv_test)
        cnt_splits = kfold.get_n_splits(pairs)
        loo = kfold.split(pairs)
        # if self.need_subsample:
        #    file_out = open("/dev/null", "a", errors="replace")
        #    loo = sklearn.cross_validation.KFold(
        #        n=len(pairs), n_folds=len(pairs) // self.size_cv_test)
        #    for max_size_train in range(10, 300, 5):
        #        finished = False
        #        my_prog = tqdm(0, total=len(loo), desc=name_category + ":" + str(max_size_train))
        #        for train, test in loo:
        #            p_test = [pairs[i] for i in test]
        #            p_train = [pairs[i] for i in train]
        #            p_train = [x for x in p_train if not self.is_pair_missing(x)]
        #            if len(p_train) <= max_size_train:
        #                finished = True
        #                continue
        #            p_train = random.sample(p_train, max_size_train)
        #            my_prog.update()
        #            self.do_test_on_pairs(p_train, p_test, file_out)
        #        if finished:
        #            break

        # my_prog = tqdm(0, total=cnt_splits, desc=name_category)
        my_prog = progressbar.ProgressBar(max_value=cnt_splits)
        cnt = 0
        for train, test in loo:
            p_test = [pairs[i] for i in test]
            p_train = [pairs[i] for i in train]
            # p_train = [x for x in p_train if not is_pair_missing(x)]
            cnt += 1
            my_prog.update(cnt)
            details += self.solver.do_test_on_pairs(p_train, p_test)

        out = dict()
        out["details"] = details
        results = {}
        if self.cnt_total_total == 0:
            results["accuracy"] = -1
        else:
            results["accuracy"] = self.cnt_total_correct / self.cnt_total_total
            results["cnt_questions_correct"] = self.cnt_total_correct
            results["cnt_questions_total"] = self.cnt_total_total
        out["result"] = results
        # str_results = json.dumps(jsonify(out), indent=4, separators=(',', ': '), sort_keys=True)
        return out

    def run(self, embs, path_dataset):  # group_subcategory
        self.embs = embs
        self.solver = select_method(self.method)(self.embs, exclude=self.exclude)


        if self.normalize:
            self.embs.normalize()
        self.embs.cache_normalized_copy()

        results = []
        dataset = Dataset(path_dataset)
        for filename in dataset.file_iterator():
            logger.info("processing " + filename)
            pairs = get_pairs(filename)
            name_category = os.path.basename(os.path.dirname(filename))
            name_subcategory = os.path.basename(filename)
            experiment_setup = dict()
            experiment_setup["dataset"] = dataset.metadata
            experiment_setup["embeddings"] = self.embs.metadata
            experiment_setup["category"] = name_category
            experiment_setup["subcategory"] = name_subcategory
            experiment_setup["task"] = "word_analogy"
            experiment_setup["default_measurement"] = "accuracy"
            experiment_setup["method"] = self.method
            experiment_setup["uuid"] = str(uuid.uuid4())
            if not self.exclude:
                experiment_setup["method"] += "_honest"
            experiment_setup["timestamp"] = datetime.datetime.now().isoformat()
            result_for_category = self.run_category(pairs)
            result_for_category["experiment_setup"] = experiment_setup
            results.append(result_for_category)
        # if group_subcategory:
            # results.extend(self.group_subcategory_results(results))
        return results

    # def group_subcategory_results(self, results):  # todo: figure out if we need this
        # group analogy results, based on the category
    #    new_results = {}
    #    for result in results:
    #        cnt_correct = 0
    #        cnt_total = 0
    #        for t in result['details']:
    #            if t['rank'] == 0:
    #                cnt_correct += 1
    #            cnt_total += 1

    #        k = result['experiment_setup']['category']

    #        if k in new_results:
    #            new_results[k]['experiment_setup']['cnt_questions_correct'] += cnt_correct
    #            new_results[k]['experiment_setup']['cnt_questions_total'] += cnt_total
    #            new_results[k]['details'] += result['details']
    #        else:
    #            new_results[k] = result.copy()
    #            del new_results[k]['experiment_setup']['category']
    #           new_results[k]['experiment_setup']['dataset'] = k
    #            # new_results[k]['experiment_setup'] = r['experiment_setup'].copy()
    #            new_results[k]['experiment_setup']['category'] = k
    #            new_results[k]['experiment_setup']['subcategory'] = k
    #            new_results[k]['experiment_setup']['cnt_questions_correct'] = cnt_correct
    #            new_results[k]['experiment_setup']['cnt_questions_total'] = cnt_total
    #    for k, v in new_results.items():
    #        new_results[k]['result'] = new_results[k]['experiment_setup']['cnt_questions_correct'] * 1.0 / new_results[k]['experiment_setup']['cnt_questions_total']
    #    out = []
    #    for k, v in new_results.items():
    #        out.append(new_results[k])
    #    return out

    #def subsample_dims(self, newdim):
        #self.embs.matrix = self.embs.matrix[:, 0:newdim]
        #self.embs.name = re.sub("_d(\d+)", "_d{}".format(newdim), self.embs.name)

    def get_result(self, embeddings, path_dataset):  # , group_subcategory=False
        if self.normalize:
            embeddings.normalize()
        results = self.run(embeddings, path_dataset)  #group_subcategory
        return results


# class SimilarToAny(PairWise):
#     def compute_scores(self, vectors):
#         scores = self.get_most_similar_fast(vectors)
#         best = scores.max(axis=0)
#         return best
#
#
# class SimilarToB(Analogy):
#     def do_test_on_pairs(self, pairs_train, pairs_test):
#         results = []
#         for p_test in pairs_test:
#             if self.is_pair_missing([p_test]):
#                 continue
#             result = self.do_on_two_pairs(p_test)
#             result["b in neighbourhood of b_prime"] = self.get_rank(p_test[0], p_test[1][0])
#             result["b_prime in neighbourhood of b"] = self.get_rank(p_test[1], p_test[0])
#             results.append(result)
#         return results
#
#     def do_on_two_pairs(self, pair_test):
#         if self.is_pair_missing([pair_test]):
#             result = self.result_miss
#         else:
#             vec_b = self.embs.get_vector(pair_test[0])
#             vec_b_prime = self.embs.get_vector(pair_test[1][0])
#             scores = self.get_most_similar_fast(vec_b)
#             result = self.process_prediction(pair_test, scores, None, None)
#             result["similarity to correct cosine"] = self.embs.cmp_vectors(vec_b, vec_b_prime)
#         return result

