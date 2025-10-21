AUTOCOMPLETE = """
CALL db.index.fulltext.queryNodes('quoteTextIndex', $q)
YIELD node AS q, score
OPTIONAL MATCH (q)-[:SAID_BY]->(a:Author)
WITH q, score, collect(DISTINCT a.name) AS authors
RETURN elementId(q)                 AS qid,
       q.short_text                 AS short_text,
       q.full_text                  AS full_text,
       coalesce(head(authors),NULL) AS author,
       score
ORDER BY score DESC
LIMIT $k
"""

DETAIL_BY_ID = """
MATCH (q:Quote)
WHERE elementId(q) = $qid
OPTIONAL MATCH (q)-[:SAID_BY]->(a:Author)
RETURN elementId(q)        AS qid,
       q.short_text        AS short_text,
       q.full_text         AS full_text,
       collect(DISTINCT a.name) AS authors,
       q.year              AS year,
       q.page              AS page,
       q.rev_id            AS rev_id,
       q.section           AS section
"""
