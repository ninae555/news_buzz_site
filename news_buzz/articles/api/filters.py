from rest_framework import exceptions
from rest_framework.filters import BaseFilterBackend

# from articles.models import Merchant, RTIEResponse


class ArticlePublisherPC1Filter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if view.action == "list":
            try:
                min_pc1 = request.query_params.get("min_pc1")
                max_pc1 = request.query_params.get("max_pc1")
                if min_pc1 is not None and max_pc1 is not None:
                    min_pc1 = float(min_pc1)
                    max_pc1 = float(max_pc1)
                    queryset = queryset.filter(publisher__pc1__gte=min_pc1, publisher__pc1__lte=max_pc1)
            except ValueError as exc:
                raise exceptions.ValidationError(
                    {"filters": "Please ensure all the filters/request query parameters have correct values"}
                ) from exc
        return queryset



