from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 100


class ScorePaginator(PageNumberPagination):
    page = DEFAULT_PAGE
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "total": self.page.paginator.count,
                "page": int(
                    self.request.GET.get("page", DEFAULT_PAGE)
                ),  # can not set default = self.page
                "page_size": int(self.request.GET.get("page_size", self.page_size)),
                "results": data,
            }
        )

    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None
        self.offset = self.get_offset(request)
        self.count = queryset.count()
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True
        if self.count == 0 or self.offset > self.count:
            return []

        # Add the limit/offset to the query
        if self.limit:
            queryset = queryset.limit(self.limit)
        if self.offset:
            queryset = queryset.offset(self.offset)

        return list(queryset.execute())
