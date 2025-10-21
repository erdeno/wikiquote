from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .neo4j_client import run_read, run_read_one, health_check_details
from .cypher import AUTOCOMPLETE, DETAIL_BY_ID

class QuoteViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="healthz")
    def healthz(self, request):
        details = health_check_details()     # {'ok': True/False, 'error': str|None}
        return Response(
            {"neo4j_ok": details["ok"], "error": details["error"]},
            status=200
        )

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        q = (request.query_params.get("q") or "").strip()
        try:
            k = int(request.query_params.get("k", 8))
        except ValueError:
            k = 8
        k = max(1, min(k, 20))
        if len(q) < 2:
            return Response([], status=200)

        rows = run_read(AUTOCOMPLETE, {"q": q, "k": k})
        hits = [{
            "quote_id": r["qid"],
            "short_text": r["short_text"],
            "full_text": r["full_text"],
            "author": r.get("author"),
            "score": r["score"],
        } for r in rows]
        return Response(hits, status=200)

    def retrieve(self, request, pk=None):
        row = run_read_one(DETAIL_BY_ID, {"qid": pk})
        if not row:
            return Response({"detail": "Not found"}, status=404)
        return Response({
            "quote_id": row["qid"],
            "short_text": row["short_text"],
            "full_text": row["full_text"],
            "authors": row.get("authors", []),
            "year": row.get("year"),
            "provenance": {
                "page": row.get("page"),
                "rev_id": row.get("rev_id"),
                "section": row.get("section"),
            }
        }, status=200)