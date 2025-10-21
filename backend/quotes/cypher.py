AUTOCOMPLETE = """
CALL db.index.fulltext.queryNodes('quoteTextIndex', $q)
YIELD node AS q, score
OPTIONAL MATCH (q)-[:SAID_BY]->(a1:Author)
OPTIONAL MATCH (q)-[:APPEARS_IN]->(:Work)<-[:BY]-(a2:Author)
WITH q, score,
     collect(DISTINCT a1.name) + collect(DISTINCT a2.name) AS all_authors
RETURN elementId(q) AS qid,
       q.text_clean AS short_text,   // <- clean display text
       q.text_clean AS full_text,    // or keep another long field if you have it
       CASE WHEN size(all_authors)>0 THEN head(all_authors) ELSE NULL END AS author,
       score
ORDER BY score DESC
LIMIT $k;
"""

DETAIL_BY_ID = """
MATCH (q:Quote)
WHERE elementId(q) = $qid
OPTIONAL MATCH (q)-[:SAID_BY]->(a1:Author)
OPTIONAL MATCH (q)-[:APPEARS_IN]->(:Work)<-[:BY]-(a2:Author)
WITH q, collect(DISTINCT a1.name) + collect(DISTINCT a2.name) AS all_authors
RETURN elementId(q) AS qid,
       q.text_clean AS short_text,
       q.text_clean AS full_text,
       all_authors  AS authors,
       q.year AS year, q.page AS page, q.rev_id AS rev_id, q.section AS section;
"""
