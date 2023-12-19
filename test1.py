import math
import jieba
import os


# 参数配置
# 第一部分
# k1：这个参数控制着词频对相似度得分的影响程度。
# k2：这个参数用于调整查询项中每个词语的权重。
# b：这个参数控制着文档长度对相似度得分的影响程度。
# 这些参数的具体取值可以根据具体的数据集和需求进行调整和优化。通常需要根据实际情况进行实验和调整，以找到最佳的参数配置，使得相似度得分能够更准确地描述查询和文档之间的相关性。

# 第二部分
# self.idf：逆文档频率（inverse document frequency）是指一个词语在整个文档集中的重要程度。
# self.avgdl：平均文档长度（average document length）是整个文档集中所有文档的平均长度。
# 这两个属性在计算 BM25 相似度得分时起到重要作用。逆文档频率用于衡量词语的重要性，平均文档长度用于调整文档长度对相似度得分的影响。具体的计算公式中会用到这些属性的值来进行相似度得分的计算。
class BM25Param:
    def __init__(self, k1=1.5, k2=1, b=0.75):
        self.k1 = k1
        self.k2 = k2
        self.b = b
        self.idf = {}  # 逆文档频率
        self.avgdl = 0  # 平均文档长度

    # 文档集中的每个文档的长度都会被统计，然后计算它们的平均值。这个平均值即为平均文档长度，用于后续的相似度计算中作为一个调整因子。
    def compute_idf(self, docs):
        n = len(docs)
        for doc in docs:
            words = set(doc)
            for word in words:
                self.idf[word] = self.idf.get(word, 0) + 1
        for word, freq in self.idf.items():
            self.idf[word] = math.log((n - freq + 0.5) / (freq + 0.5))

        sum_len = 0
        for doc in docs:
            sum_len += len(doc)
        self.avgdl = sum_len / n


# 计算
class BM25:
    def __init__(self, docs_path=None):
        self.params = BM25Param()
        self.docs = []
        if docs_path is None:
            docs_path = "data/test1.txt"
        self.load_documents(docs_path)
        self.params.compute_idf([doc for doc, _, _ in self.docs])  # 调用compute_idf方法计算idf值

    def load_documents(self, docs_path):
        with open(docs_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                doc, view_count, behavior = line.split('&')
                self.docs.append((doc, int(view_count), behavior))

    # 在 compute_similarity 方法中，它使用 BM25 公式计算查询词语和文档之间的相似度得分。其中还考虑了文档的浏览量和用户行为等因素的加权。
    def compute_similarity(self, query):
        scores = []
        for doc, view_count, behavior in self.docs:
            score = 0
            words = list(jieba.cut(query))
            doc_words = list(jieba.cut(doc))
            for word in words:
                if word not in doc_words:
                    continue
                tf = doc_words.count(word) / len(doc_words)
                idf = self.params.idf.get(word, 0)
                score += (idf * tf * (self.params.k1 + 1)) / (tf + self.params.k1 * (
                            1 - self.params.b + self.params.b * len(doc_words) / self.params.avgdl))

                # 添加诗歌浏览量、用户行为等因素的加权
                # 根据具体需求来确定权重系数和计算方式
                if behavior == "点赞":
                    score *= 1.2
                elif behavior == "收藏":
                    score *= 1.5

                score *= math.log(view_count + 1)

            scores.append((doc, score))

        return scores

    # 而 compute_similarity_rank 方法则基于相似度得分对文档进行排序，返回排序后的结果。
    def compute_similarity_rank(self, query):
        scores = self.compute_similarity(query)
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores


if __name__ == "__main__":
    bm = BM25()
    query = "白日依山尽"
    result = bm.compute_similarity_rank(query)
    print("查询结果：")
    for doc, score in result:
        print(f"文档：{doc}，得分：{score}")