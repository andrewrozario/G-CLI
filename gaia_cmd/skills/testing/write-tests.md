# SKILL: Write Tests
# DESCRIPTION: Specialized logic for creating comprehensive unit and integration tests.
# TAGS: testing, pytest, jest, coverage, unit-test
# REQUIRED_TOOLS: write_file, run_shell_command, read_file

## Specialized Instructions
1.  **Identify Boundary Conditions**: When writing tests, focus on edge cases (empty inputs, large data, nulls, error states).
2.  **Test Isolation**: Ensure tests do not depend on external state. Use mocks/stubs for external API calls or database connections.
3.  **Naming Convention**: Use descriptive test names (e.g., `test_should_reject_invalid_email_format`).
4.  **Coverage Goal**: Aim for branch coverage, not just line coverage.
5.  **Autonomous Run**: Always try to run the newly created tests using the appropriate runner (e.g., `pytest`, `npm test`) to verify they actually work.
