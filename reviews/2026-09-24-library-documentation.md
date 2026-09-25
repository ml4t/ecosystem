# Six-library documentation review, 2026-09-24

## Finding

All six local documentation sites build strictly, but they do not yet give readers the same quality
of route from a task to a tested example, a public API, and a relevant book notebook. Backtest is the
strongest reference for executable guidance and checked book links. The other sites have useful
content and broadly similar navigation, but most book references are plain paths, some paths have
drifted, and example verification differs by repository.

This review covers Data, Engineer, Models, Diagnostic, Backtest, and Live. Specs remains part of the
ecosystem's release standard but has no development sidecar and is outside this six-site campaign.

## Evidence and limits

- Source: local release checkouts on 2026-09-24. Engineer, Models, Diagnostic, Backtest, and Live
  were clean at `main`, matching their configured upstream tracking branches. Data was clean at
  `docs/market-alt-sources`; that branch was three commits ahead of and one commit behind the local
  `origin/main` ref. Data's page inventory is therefore branch-specific.
- Book path comparison: the local public companion checkout
  `stefan-jansen/machine-learning-for-trading` at commit
  [`d2edec5`](https://github.com/stefan-jansen/machine-learning-for-trading/tree/d2edec54b1c7a6a9d7a97d8129eb05db4491e1eb).
  The check matched literal `.py` and `.ipynb` paths in each Book Guide, allowing the obsolete
  `code/` prefix to be removed. Template paths such as `<study>` were counted as unresolved. This
  is a path check, not a semantic validation of every book mapping.
- Build: `uv run mkdocs build --strict` passed in all six checkouts during this review.
- Backtest checks: `validation/check_book_links.py` passed for 22 companion paths at commit
  `366e1d51ace2d851776499a68da3d6e3c2641b02`; `validation/check_documentation_links.py`
  checked 2,005 rendered content links and 29 external destinations; and
  `validation/check_documentation_examples.py` ran its 23 selected examples successfully.
- This review did not run each library's full tests, execute every code block, check all external
  destinations in the other five sites, or compare deployed pages with these checkouts.

| Library | Markdown pages | User-guide pages | Tutorials | Book Guide | Strict build | Main finding |
|---|---:|---:|---:|---|---|---|
| Data | 60 | 6 | 6 | Yes | Pass | Broad provider coverage and offline quickstart; book references are plain text and several paths have changed. |
| Engineer | 14 | 8 | 0 | Yes | Pass | Substantial feature, label, and bar guides; none of 17 concrete book file paths resolves in the current companion tree; three case-study paths are templates. |
| Models | 19 | 9 | 0 | Yes | Pass | Strong model-family and contract explanations; six named book files resolve, but the guide provides no direct file links and its first workflow is costly. |
| Diagnostic | 22 | 9 | 0 | Yes | Pass | Good method pages and synthetic quickstart; seven of 26 named book file paths checked here are stale. |
| Backtest | 28 | 13 | 9 | Yes | Pass | Complete tutorial sequence, checked output, and pinned book links; use as the initial quality reference, then review coverage against the full released API. |
| Live | 16 | 8 | 0 | Yes | Pass | Practical broker, feed, risk, and operator guides; three of 14 named book file paths checked here are stale, and the first run requires credentials even in shadow mode. |

Page counts include material outside primary navigation. They measure inventory, not quality.

## Cross-library issues

1. **Book navigation.** Backtest links directly to a fixed book revision and verifies the files.
   The other five Book Guides predominantly list paths without clickable links. Engineer's chapter
   names and numbering reflect an older book tree: for example, the current companion file is
   `03_market_microstructure/14_itch_bar_sampling.py`, while its guide names
   `03_market_microstructure/code/08_itch_bar_sampling.py`. A reader cannot rely on those paths.
2. **Example evidence.** Every site builds, but a strict build does not execute Python examples.
   Backtest has an installed-wheel runner with expected output for selected workflows. The other
   sites need evidence for their own principal examples, scaled to optional services and hardware.
3. **First use.** Data, Backtest, and Diagnostic provide local or synthetic first runs. Engineer's
   quickstart uses synthetic data but lacks a recorded expected result. Models opens with a sizeable
   IPCA workflow, then shows longer neural training. Live's recommended shadow-mode code still
   instantiates credentialed Alpaca adapters. Each site needs a visible success criterion and an
   offline path where the package can support one.
4. **Content depth.** The sites share Home, Getting Started, User Guide, API Reference, and Book
   Guide in navigation. Backtest adds a linked tutorial sequence. Diagnostic adds statistical
   method explanations. Data adds provider catalogues. Equal quality should be judged by task
   completion, public API accuracy, and tested examples rather than identical sections or lengths.
5. **Maintained predecessors.** The six sites rarely explain how a reader using Zipline, Alphalens,
   or Pyfolio should evaluate a relevant successor workflow. A factual task-by-task comparison is
   needed before adding notices to the older repositories. Zipline, Alphalens, and Pyfolio should
   not be described as discontinued or fully replaceable without evidence.

## Review sequence

1. Backtest checks its current guide against the complete released public surface and documents
   any remaining gaps. Keep its example and link checks as the reference pattern.
2. Engineer repairs the book map first, followed by Diagnostic, Live, Data, and Models. Each checks
   notebook meaning, not only file existence, and links from principal task pages.
3. Each library records a capability-to-guide-to-reference-to-example inventory, then fills gaps
   in task order. Review rendered pages and example output before publishing.
4. The ecosystem rechecks all six sites against the shared standard and records any exceptions.
   The older repository maintainers can then add scoped successor notices with verified migration
   examples.
