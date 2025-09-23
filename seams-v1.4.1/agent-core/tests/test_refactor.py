from my_agent.tools.tool_refactor import refactor_python_function, RefactorInput

def test_refactor_smoke():
    out = refactor_python_function(RefactorInput(code="def f(x):return x+1", goal="clarify", constraints=["pep8"], seed=42))
    assert hasattr(out, "code") and hasattr(out, "notes")
