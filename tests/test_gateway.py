import httpx
import pytest

from llm import gateway as gateway_module
from llm.gateway import AIGateway


class FakeResponse:
    def __init__(self, data, error=None):
        self._data = data
        self._error = error

    def raise_for_status(self):
        if self._error:
            raise self._error

    def json(self):
        return self._data


class FakeClient:
    def __init__(self, response=None):
        self.posts = []
        self.response = response

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def post(self, url, json=None, headers=None):
        self.posts.append((url, json, headers))
        return self.response


@pytest.fixture
def client(monkeypatch, config):
    monkeypatch.setattr(config, "api_gateway_url", "http://gw.test")
    monkeypatch.setattr(config, "api_gateway_key", "secret-key")
    monkeypatch.setattr(config, "default_model", "the-default")
    fake = FakeClient(response=FakeResponse({"choices": [{"message": {"content": "answer"}}]}))
    monkeypatch.setattr(gateway_module.httpx, "Client", lambda **_: fake)
    return fake


def test_chat_raises_value_error_without_message_or_messages(client):
    with pytest.raises(ValueError, match="message"):
        AIGateway().chat()

    assert client.posts == []


def test_chat_wraps_single_message_as_one_user_turn(client):
    AIGateway().chat("hello")

    assert client.posts[0][1]["messages"] == [{"role": "user", "content": "hello"}]


def test_chat_sends_messages_list_as_given(client):
    turns = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]

    AIGateway().chat(messages=turns)

    assert client.posts[0][1]["messages"] == turns


def test_chat_posts_to_gateway_chat_completions_url_with_api_key_header(client):
    AIGateway().chat("hello")

    url, _, headers = client.posts[0]
    assert url == "http://gw.test/ai/v1/chat/completions"
    assert headers == {"X-API-Key": "secret-key"}


def test_chat_strips_trailing_slash_from_gateway_url(client, config, monkeypatch):
    monkeypatch.setattr(config, "api_gateway_url", "http://gw.test/")

    AIGateway().chat("hello")

    assert client.posts[0][0] == "http://gw.test/ai/v1/chat/completions"


def test_chat_uses_default_model_when_no_model_given(client):
    AIGateway().chat("hello")

    assert client.posts[0][1]["model"] == "the-default"


def test_chat_uses_given_model_over_default(client):
    AIGateway().chat("hello", model="other-model")

    assert client.posts[0][1]["model"] == "other-model"


def test_chat_returns_first_choice_message_content(client):
    client.response = FakeResponse(
        {"choices": [{"message": {"content": "first"}}, {"message": {"content": "second"}}]}
    )

    assert AIGateway().chat("hello") == "first"


def test_chat_raises_when_gateway_returns_http_error(client):
    request = httpx.Request("POST", "http://gw.test")
    error = httpx.HTTPStatusError("bad", request=request, response=httpx.Response(500, request=request))
    client.response = FakeResponse({}, error=error)

    with pytest.raises(httpx.HTTPStatusError):
        AIGateway().chat("hello")
