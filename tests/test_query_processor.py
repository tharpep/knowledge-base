import pytest

from rag.query_processor import QueryProcessor


class FakeGateway:
    def __init__(self, answer=None, error=None):
        self.answer = answer
        self.error = error
        self.calls = []

    def chat(self, message, model=None):
        self.calls.append((message, model))
        if self.error:
            raise self.error
        return self.answer


@pytest.mark.parametrize("query", ["", "abcd", "  ab  ", "     "])
def test_expand_returns_query_under_5_characters_without_calling_gateway(query):
    gateway = FakeGateway(answer="a much longer expansion of everything")

    assert QueryProcessor(gateway=gateway).expand(query) == query
    assert gateway.calls == []


def test_expand_calls_gateway_for_query_of_exactly_5_characters():
    gateway = FakeGateway(answer="abcde and many related terms")

    result = QueryProcessor(gateway=gateway).expand("abcde")

    assert result == "abcde and many related terms"
    assert len(gateway.calls) == 1


def test_expand_returns_longer_expansion_stripped():
    gateway = FakeGateway(answer="\n  python async programming tutorial  \n")

    assert QueryProcessor(gateway=gateway).expand("python async") == "python async programming tutorial"


def test_expand_prompt_contains_original_query():
    gateway = FakeGateway(answer="python async programming tutorial")

    QueryProcessor(gateway=gateway).expand("python async")

    assert "python async" in gateway.calls[0][0]


def test_expand_falls_back_to_original_when_gateway_raises():
    gateway = FakeGateway(error=RuntimeError("boom"))

    assert QueryProcessor(gateway=gateway).expand("python async") == "python async"


def test_expand_falls_back_to_original_when_answer_is_shorter():
    gateway = FakeGateway(answer="python")

    assert QueryProcessor(gateway=gateway).expand("python async") == "python async"


def test_expand_falls_back_to_original_when_answer_is_empty():
    gateway = FakeGateway(answer="   ")

    assert QueryProcessor(gateway=gateway).expand("python async") == "python async"


def test_expand_falls_back_to_original_when_answer_is_same_length():
    gateway = FakeGateway(answer="PYTHON ASYNC")

    assert QueryProcessor(gateway=gateway).expand("python async") == "python async"


def test_expand_passes_call_model_over_constructor_model():
    gateway = FakeGateway(answer="python async programming tutorial")

    QueryProcessor(gateway=gateway, model="default-m").expand("python async", model="call-m")

    assert gateway.calls[0][1] == "call-m"


def test_expand_uses_constructor_model_when_none_given():
    gateway = FakeGateway(answer="python async programming tutorial")

    QueryProcessor(gateway=gateway, model="default-m").expand("python async")

    assert gateway.calls[0][1] == "default-m"
