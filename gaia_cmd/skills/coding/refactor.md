# SKILL: Refactor Code
# DESCRIPTION: Specialized logic for improving code structure without changing behavior.
# TAGS: refactor, cleanup, technical-debt, modularize
# REQUIRED_TOOLS: read_file, edit_file, run_shell_command

## Specialized Instructions
1.  **Analyze Dependencies**: Before changing a function, find all its call sites using `grep_search` or `run_shell_command`.
2.  **Small Incremental Changes**: Never refactor an entire file at once. Use `edit_file` for targeted, atomic changes.
3.  **Preserve Signatures**: If you must change a function signature, ensure all callers are updated in the same task.
4.  **Verification**: After every edit, run the project's test suite to ensure zero regressions.
5.  **Clean Code Principles**: Prioritize SOLID principles and DRY (Don't Repeat Yourself).
