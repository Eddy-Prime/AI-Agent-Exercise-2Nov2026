from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize(text):
    text = text.lower().replace("\u2019", "'")
    for dash in ("\u2010", "\u2011", "\u2013"):
        text = text.replace(dash, "-")
    return " ".join(text.split()).replace(" %", "%")


class Retriever:
    """Finds the chunks that best match a question (TF-IDF word matching + cosine similarity)."""

    def __init__(self, chunks):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words="english", sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform([c["text"] for c in chunks])

    def search(self, query, top_k, threshold=0.0):
        scores = cosine_similarity(self.vectorizer.transform([query]), self.matrix)[0]
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        results = []
        for i in ranked[:top_k]:
            if scores[i] <= 0 or scores[i] < threshold:
                continue
            results.append({**self.chunks[i], "score": float(scores[i])})
        return results


def evidence_hit(retrieved, evidence):
    """True if every evidence phrase appears in the retrieved text. None if there is no evidence."""
    if not evidence:
        return None
    joined = normalize(" ".join(r["text"] for r in retrieved))
    return all(normalize(e) in joined for e in evidence)
