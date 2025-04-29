from unittest.mock import MagicMock, Mock

from imednet.core.paginator import Paginator


class TestPaginator:
    def test_init(self):
        client = Mock()
        path = "/api/test"
        params = {"param1": "value1"}

        paginator = Paginator(client, path, params)

        assert paginator.client == client
        assert paginator.path == path
        assert paginator.params == params
        assert paginator.page_size == 100
        assert paginator.page_param == "page"
        assert paginator.size_param == "size"
        assert paginator.data_key == "data"
        assert paginator.metadata_key == "metadata"
        assert id(paginator.params) != id(params)  # Check params were copied

    def test_params_none(self):
        client = Mock()
        paginator = Paginator(client, "/api/test")
        assert paginator.params == {}

    def test_iteration_single_page(self):
        client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [{"id": 1}, {"id": 2}],
            "pagination": {"totalPages": 1},
        }
        client.get.return_value = mock_response

        paginator = Paginator(client, "/api/test")
        results = list(paginator)

        assert results == [{"id": 1}, {"id": 2}]
        client.get.assert_called_once_with("/api/test", params={"page": 0, "size": 100})

    def test_iteration_multiple_pages(self):
        client = Mock()
        responses = [
            {"data": [{"id": 1}, {"id": 2}], "pagination": {"totalPages": 3}},
            {"data": [{"id": 3}, {"id": 4}], "pagination": {"totalPages": 3}},
            {"data": [{"id": 5}], "pagination": {"totalPages": 3}},
        ]

        # Configure mock to return different responses each time it's called
        client.get = MagicMock(
            side_effect=[
                Mock(json=lambda: responses[0]),
                Mock(json=lambda: responses[1]),
                Mock(json=lambda: responses[2]),
            ]
        )

        paginator = Paginator(client, "/api/test")
        results = list(paginator)

        assert results == [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}]
        assert client.get.call_count == 3

        # Check that page number was incremented correctly
        client.get.assert_any_call("/api/test", params={"page": 0, "size": 100})
        client.get.assert_any_call("/api/test", params={"page": 1, "size": 100})
        client.get.assert_any_call("/api/test", params={"page": 2, "size": 100})

    def test_empty_data(self):
        client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"pagination": {"totalPages": 1}}
        client.get.return_value = mock_response

        paginator = Paginator(client, "/api/test")
        results = list(paginator)

        assert results == []

    def test_custom_parameters(self):
        client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [{"id": 1}, {"id": 2}],
            "pagination": {"totalPages": 1},
        }
        client.get.return_value = mock_response

        paginator = Paginator(
            client, "/api/test", page_param="pageNumber", size_param="pageSize", data_key="items"
        )
        results = list(paginator)

        assert results == [{"id": 1}, {"id": 2}]
        client.get.assert_called_once_with("/api/test", params={"pageNumber": 0, "pageSize": 100})

    def test_no_pagination_info(self):
        client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"data": [{"id": 1}, {"id": 2}]}
        client.get.return_value = mock_response

        paginator = Paginator(client, "/api/test")
        results = list(paginator)

        assert results == [{"id": 1}, {"id": 2}]
        client.get.assert_called_once()
