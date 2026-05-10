# AGENT.md - Python Style Guide

These guidelines define how Python code in this repository should be generated and maintained.

Priority: **clarity, maintainability, and consistency**.

---

## 1. General Style

- Follow **PEP8** as the primary guideline.

- Write **explicit and easy-to-read** code.

- Avoid complex solutions if a simple one suffices.

- Do not optimize performance unless necessary.

---

## 2. Formatting

- Use **4 spaces** for indentation (never tabs).

- Keep lines preferably under **88 characters**.

- Leave spaces around operators.
- Use blank lines to separate logical blocks.

- Separate high-level functions with **2 blank lines**.

- ---

## 3. Naming Conventions

- Variables and functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_CASE`
- Modules/files: `snake_case.py`

Rules:
- Use descriptive names.

- Don't use unnecessary abbreviations.

- Avoid generic names like `data`, `temp`, `value` if they don't provide context.

- ---

## 4. Typing and Annotations

- Use type hints whenever possible.

- Always type arguments and return values ​​in public functions.

- Use modern types (`list[str]`, `dict[str, int]`) in Python 3.9+.

- Use `Optional[T]` only if the value can actually be `None`.

---

## 5. Docstrings and Documentation

* Every public function must have a docstring.

* Keep docstrings short and useful.

* Don't repeat obvious information if the function name already explains it.

---

## 6. Imports

* Don't use `import *`.

* Mandatory order:

1. Standard library

2. Third-party

3. Local imports
* Separate groups of imports with a blank line.

---

## 7. Functions and Complexity

* Each function should do **only one thing**.

* Avoid long functions (ideally less than 30 lines).

* Avoid deep nesting.

* Use `early return` whenever possible.

* Avoid complicated logic on a single line.

---

## 8. Classes and Design

* Don't use classes if a single function is sufficient.

* Avoid classes with too many responsibilities.

--- * Prefer composition over inheritance.

* Use `@dataclass` for simple data structures.

---

## 9. Error Handling

* Don't use generic `except:`.

* Catch specific exceptions.

* If you rethrow an exception, add useful context.

* Don't ignore errors without justification.

---

## 10. Logging

* Use `logging` instead of `print`.

* Don't log secrets (passwords, tokens, keys).

* Messages should include useful context.

---

## 11. Testing

* Write tests using `pytest`.

* Tests must be:

* deterministic

* fast

* independent

Convention:

* Files: `test_*.py`
* Functions: `test_should_do_something()`

---

## 12. Security Rules

* Do not hardcode secrets.

* Validate all external input.

* Do not use `eval()` or `exec()`.

* Do not execute system commands without sanitization.

---

## 13. Recommended Project Structure

* Separate business logic from infrastructure.

* Keep code modular and easy to test.

---

## 14. Final Rule

Priority:

1. Clarity
2. Maintainability
3. Correctness
4. Performance (only if applicable)

---