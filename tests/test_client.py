import pytest

from http_fixture import fixture_server
from nviq_lemonade.client import LemonadeClient
from nviq_lemonade.errors import LemonadeError


def test_client_calls_required_and_optional_lemonade_endpoints():
    with fixture_server() as (base_url, _handler):
        client = LemonadeClient(base_url)
        assert client.health()["status"] == "ok"
        assert client.models()[0]["id"] == "Fixture-Model"
        completion = client.chat("Fixture-Model", [{"role": "user", "content": "hello"}])
        assert completion["choices"][0]["message"]["content"] == "fixture response"
        assert client.stats()["tokens_per_second"] == 42.0
        assert client.system_info()["os"] == "fixture-os"


def test_client_sends_api_key_as_bearer_token():
    with fixture_server() as (base_url, handler):
        client = LemonadeClient(base_url, api_key="test-key")
        client.health()
        assert handler.last_authorization == "Bearer test-key"


def test_client_normalizes_http_errors():
    with fixture_server() as (base_url, _handler):
        client = LemonadeClient(base_url)
        with pytest.raises(LemonadeError, match="HTTP 500"):
            client.chat("Error-Model", [{"role": "user", "content": "hello"}])
