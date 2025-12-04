# backend/quotes/cypher.py

# Using fulltext index (faster)
AUTOCOMPLETE = """
CALL db.index.fulltext.queryNodes('quoteTextIndex', $q)
YIELD node AS q, score
MATCH (q)-[:SAID]-(a:Author)
RETURN elementId(q) AS qid,
       q.text_clean AS short_text,
       q.text_clean AS full_text,
       a.name AS author,
       score
ORDER BY score DESC
LIMIT $k
"""

DETAIL_BY_ID = """
MATCH (q:Quote)-[:SAID]-(a:Author)
WHERE elementId(q) = $qid
RETURN elementId(q) AS qid,
       q.text_clean AS short_text,
       q.full_text AS full_text,
       collect(a.name) AS authors,
       null AS year,
       null AS page,
       null AS rev_id,
       null AS section
"""