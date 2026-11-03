# Test conventions

- **Never touch real credentials, the network, or your home directory.** An autouse fixture
  in `conftest.py` fails the test (with `pytest.fail`, which tool code can't swallow) if it
  builds a real Canvas client, reads a browser's real cookie store (reading a fixture
  `cookie_file=` is allowed), or sends an HTTP request. `HOME` points at a temp directory.
- **Use autospecced fakes.** Use the `mock_client` fixture, or
  `mock.create_autospec(CanvasClient, instance=True)` where a module needs its own patch.
  Stubbing a client method that doesn't exist then fails. Configure methods through
  `.return_value` and `.side_effect`: assigning a new attribute isn't checked.
- **Assert behavior, not mocks.** A test must fail when the code under test breaks. Check
  that every stubbed input field comes out mapped, and check the arguments the code sends
  to the client. Don't assert only a mock's own return value, that an `"error"` key
  exists, or that `main()` calls `app()`.
- **Assert exact values.** Prefer a specific error code or `==` over `"error" in result`
  or `len(x) > 0`.
- **Validate arguments in one place.** `dispatch_tool_call` rejects missing required
  arguments and wrong types from each tool's schema before the tool runs.
  `test_registry.py` pins every tool's required arguments and checks that each missing one
  is rejected without calling the tool's code. Don't add per-tool "requires X" tests.
- **No duplicates.** If two tests fail for exactly the same bugs, keep the stronger one or
  parametrize.
- **Use real local dependencies when cheap:** `tmp_path` stores, SQLite cookie files,
  `requests` request preparation, `CliRunner`.
