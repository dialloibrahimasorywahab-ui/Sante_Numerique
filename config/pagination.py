from math import ceil
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "page"

    def get_paginated_response(self, data):
        total_count = self.page.paginator.count
        page_size = self.get_page_size(self.request) or self.page_size
        total_pages = ceil(total_count / page_size) if page_size else 1

        return Response({
            "count": total_count,
            "total_pages": total_pages,
            "current_page": self.page.number,
            "page_size": page_size,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        })


def paginate_response(queryset, request, serializer_class, context=None):
    """
    Helper pour paginer facilement une liste ou un QuerySet dans une vue @api_view.
    Retourne une Response paginée conforme à StandardResultsSetPagination.
    """
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(queryset, request)
    ctx = context or {"request": request}

    if page is not None:
        serializer = serializer_class(page, many=True, context=ctx)
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True, context=ctx)
    return Response(serializer.data)
