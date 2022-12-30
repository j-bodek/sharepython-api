from rest_framework import pagination
from rest_framework.response import Response
from typing import Type


class PageNumberPagination(pagination.PageNumberPagination):
    """
    Extend PageNumberPagination to allow specifying page size, and
    return current page and number of pages
    """

    page_size_query_param = "page_size"

    def get_paginated_response(self, data) -> Type[Response]:
        return Response(
            {
                "next": self.page.next_page_number() if self.page.has_next() else None,
                "previous": self.page.previous_page_number()
                if self.page.has_previous()
                else None,
                "count": self.page.paginator.count,
                "current_page": self.page.number,
                "num_pages": self.page.paginator.num_pages,
                "results": data,
            }
        )
