# Contributing

These requirements apply to the current ML4T libraries and the maintained Zipline, Pyfolio,
Alphalens, and Empyrical Reloaded repositories. Use the repository that owns the affected code.
Shared policy and qualification belong in `ml4t/ecosystem`; library changes belong in that library.

## Start with one issue

Search existing issues before opening a new one. Each issue describes one problem or coherent
change. Open separate issues for unrelated problems.

For a bug, include the affected package version, environment, expected behavior, observed behavior,
and the smallest complete reproduction. Report suspected vulnerabilities through the private
process in [SECURITY.md](SECURITY.md).

Discuss substantial changes in the owning issue before implementing them. Reloaded libraries accept
bug, security, and compatibility fixes; direct new feature requests to the current ML4T libraries.

## Submit one focused pull request

Each pull request addresses one issue and includes a closing reference, such as `Closes #123`.
Related code, tests, and documentation can belong in the same PR. Keep unrelated fixes, refactors,
and formatting changes separate. Automated dependency updates and administrative metadata changes
do not require a separate issue.

For a bug fix, include a regression that exercises the affected public API or user workflow. Run it
against the relevant base revision and the proposed fix, and record both revisions, commands, and
results. It must fail because of the defect on the base and pass with the fix. Tests of copied logic
or source text do not establish that the behavior is corrected.

Run the owning repository's documented quality checks before requesting review and report the
commands and results. Documentation changes need documentation checks; they do not need an
artificial regression test. This repository's commands are in [AGENTS.md](AGENTS.md).

Verified defects must be corrected, including defects that affect numerical results. If a proposed
change alters an intended definition, annualization, sign convention, or default, agree on the
expected behavior in the owning issue and document its compatibility impact. Existing output alone
is not evidence that the implementation is correct.

## AI assistance and accountability

You may use AI tools for code and prose. State whether you used them and which parts they helped
produce. Review and test the submission yourself, and be able to explain the code, evidence, and
responses you submit. An automated reply does not replace understanding a review question.

Keep concurrent submissions manageable. Wait for feedback on your first focused contribution
before opening a large series of similar PRs.

Maintainers may ask you to split or complete a submission, or close it without detailed review when
it does not meet these requirements. You are welcome to resubmit once it does. Existing bundled PRs
may contain useful fixes; maintainers can request focused replacements so each fix can be assessed
independently.
