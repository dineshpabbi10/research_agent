---
name: python_best_practices
description: "Provides Python best practices, pytest-mock (`mocker`) examples, and LangChain/LangGraph guidance for agents."
tags: [python, testing, pytest-mock, langchain, langgraph, skill]
version: 1.0
---

# Python Best Practices Skill

Purpose: concise, machine-readable guidance and small runnable snippets that developer agents can read and surface to developers.

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

## Mocker (pytest-mock) example

Agents may extract or display this snippet when suggesting tests.

```python
def test_call_external_service_with_mocker(mocker):
    mock_service = mocker.Mock()
    mock_service.get.return_value = {"ok": True}

    result = mock_service.get("my-resource")

    assert result == {"ok": True}
    mock_service.get.assert_called_once_with("my-resource")
```

Notes: prefer `mocker.Mock()` or `mocker.patch()` to replace external clients and assert interactions.

## LangChain quick snippet

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

## How agents should read this file

- Parse the YAML frontmatter for metadata.
- Extract `Machine-friendly summary` for capabilities.
- Provide the code snippets verbatim when offering examples.

## Attribution

Generated for internal developer assistance; safe to surface to contributors.
