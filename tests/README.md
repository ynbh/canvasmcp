# Test conventions

- **Never touch real credentials.** An autouse fixture makes any attempt to build a real
  Canvas client fail. Use the `mock_client` fixture, which is autospecced from
  `CanvasClient`, so stubbing a method that doesn't exist fails.
- **Assert behavior, not mocks.** A test must fail when the code under test breaks. Don't
  assert only that a mock's return value came back, that some `"error"` key exists, or
  that `main()` calls `app()`.
- **Assert exact values.** Prefer `== {...}` or a specific error code over `"error" in result`
  or `len(x) > 0`.
- **Validate arguments in one place.** Required arguments and types are enforced by
  `dispatch_tool_call` from each tool's schema; `test_registry.py` checks that for every
  tool. Don't add per-tool "requires X" tests.
- **One behavior per test, no duplicates.** If two tests would fail for the same bug,
  keep the stronger one or parametrize.
- **Use real local dependencies when cheap:** `tmp_path` stores, SQLite cookie files,
  `requests` request preparation, `CliRunner`.
