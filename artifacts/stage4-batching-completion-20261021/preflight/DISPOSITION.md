# Initial preflight launcher failure

No live model requests were made. Python unittest discovery rejected the tests
directory when an explicit top-level package directory was supplied; this
checkout uses namespace-importable tests without a package initializer.

The launcher was corrected to the repository's existing discovery convention.
The next attempt uses a separately named directory, preflight-validated. This
initial directory is preserved and is not counted as a completed acceptance run.
