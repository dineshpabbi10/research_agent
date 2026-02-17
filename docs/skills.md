# Python Best Practices Skill

This page provides a concise, agent-friendly summary of the `python_best_practices` skill.

## Machine-friendly summary

```yaml
skill: python_best_practices
provides:
  - best_practices_checklist
  - pytest_mocker_example
  - langchain_snippet
  - langgraph_notes
```

## Best-practices checklist

- Use type hints for public APIs.
- Prefer `@dataclass` for small data holders.
- Keep functions small and pure where possible.
- Write focused unit tests and use `pytest`.
- Use `pytest-mock` (the `mocker` fixture) for lightweight mocking.
- Enforce formatting/linting with `black`, `ruff`, and `isort` in CI and pre-commit.

## Mocker example

```python
def test_call_external_service_with_mocker(mocker):
    mock_service = mocker.Mock()
    mock_service.get.return_value = {"ok": True}

    result = mock_service.get("my-resource")

    assert result == {"ok": True}
    mock_service.get.assert_called_once_with("my-resource")
```

## LangChain snippet

```python
from langchain import OpenAI, LLMChain, PromptTemplate

prompt = PromptTemplate(input_variables=["topic"], template="Write a short summary about {topic}.")
llm = OpenAI()
chain = LLMChain(llm=llm, prompt=prompt)
print(chain.run({"topic": "unit testing with mocker"}))
```

## LangGraph notes

- Keep node logic small and injectable so agents can auto-generate unit tests.
- Provide adapters for external services so they can be mocked in CI.
- Add lightweight integration fixtures to validate graph wiring.
