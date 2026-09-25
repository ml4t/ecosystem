# Documentation

Each library owns its user and API documentation. The ecosystem owns the shared publication
requirements and index.

## Public repository and package metadata

The release repository, built distributions, PyPI project, documentation site, and GitHub settings
must identify the same library. An audit passes only when all of the following are true:

- `pyproject.toml` contains the exact author and maintainer names and addresses in
  `config/libraries.toml`;
- the package description and GitHub description are the same factual sentence, within the
  configured character limits, and state what the library provides;
- the description contains no unsupported performance, quality, adoption, or completeness claim;
- package keywords include every configured common keyword, at least two terms specific to the
  library's responsibility, and meet the configured minimum count without duplicates;
- package classifiers include every configured classifier plus the operating systems actually
  exercised by release qualification;
- project URLs use every configured label and resolve to the library documentation, repository,
  issue tracker, and release notes or changelog;
- the GitHub homepage is the canonical documentation route and its topics include every configured
  common topic plus terms specific to the library; and
- the latest PyPI metadata matches the source and built wheel for description, people, license,
  Python requirement, classifiers, keywords, and project URLs.

Public metadata and prose must not contain placeholder identities, fabricated support
addresses, template project names, or references to organizations that do not own the library.
Historical names belong only in migration notes when a reader needs them.

## README contract

The root README must let a new user decide whether the library applies, install it, complete one
representative task, and find authoritative detail. It passes when it contains:

- the same responsibility statement used by package and GitHub metadata;
- supported Python versions and one installation command using the published distribution name;
- a minimal quick start that imports the public package and exercises a supported primary workflow;
- explicit optional-dependency, external-service, hardware, and support boundaries where they
  affect the quick start or normal use;
- links to the documentation, issue tracker, license, release notes or changelog, and only the
  related ML4T libraries needed to explain integration;
- development setup and the repository's authoritative quality-gate command or commands; and
- no stale versions, paths, output, badges, APIs, project names, or unverified comparative claims.

README commands and examples are behavior, not decoration. CI must install from the built wheel in
a clean environment and run the documented import and quick start. Link checking must cover every
README link. Text searches alone do not prove that an example works.

## Required information architecture

Each published library site contains, where applicable:

- a concise product and responsibility statement;
- installation and first successful use;
- task-oriented user guides;
- explanations of important semantics and design decisions;
- API reference generated from the released public interface;
- executable examples using supported APIs;
- compatibility, optional-dependency, and hardware limitations;
- migration guidance for incompatible changes; and
- links to related ML4T libraries without implying false dependencies.

Use the Diataxis categories deliberately: tutorials teach a first successful workflow, how-to
guides solve named tasks, reference pages describe the public interface, and explanations document
semantics and design decisions. A page should have one primary purpose. The README remains a concise
entry point rather than a duplicate documentation site.

## Reader and content standard for the six user-facing libraries

Data, Engineer, Models, Diagnostic, Backtest, and Live must give readers the same level of guidance
for their respective responsibilities. Equal quality does not require equal page counts. Each site
must let a new reader answer these questions without reading source code:

1. What problem does this package solve, and which adjacent package owns a different step?
2. What can I run first with the released package and without private data or credentials?
3. How do I perform each principal supported task with my own input?
4. Which defaults, input contracts, timing rules, failure modes, and limits affect the result?
5. Where are the exact public signatures and supported options?
6. Which public book notebook or case study explains the method or shows a fuller application?

The home page routes to installation, a completed first workflow, task guides, API reference, and
book examples. The first workflow includes its input, complete command or program, expected result,
and an explanation of that result. A task guide states its preconditions, the steps, how to verify
the result, relevant decisions or pitfalls, and links to the API reference. Explanation pages cover
semantics that a short recipe would conceal, such as temporal alignment, statistical assumptions,
execution order, persistence, and safety boundaries. Reference pages cover the released public
interface uniformly; a guide need not repeat every parameter.

Each library maintains a capability-to-documentation inventory during review. For every principal
supported workflow, it identifies the task guide, public API reference, and runnable example. An
optional provider, broker, accelerator, or paid data source can use a separate example, but its
requirements and an offline path must be explicit. The inventory also marks experimental features,
unsupported operations, and migration routes. Do not describe an experimental feature as a normal
default or imply that adjacent libraries are required when they are optional.

Examples must import the published package API, use representative data with stated assumptions,
and show output or an observable assertion. Run the primary quickstart and representative workflows
from a built wheel in a clean environment. Compare documented output where deterministic. Check
optional-service examples with the narrowest safe verification available, and label any part that
cannot run without credentials or hardware. A strict MkDocs build alone does not verify example
behavior or external links.

## Book and case-study links

The six sites use *Machine Learning for Trading, Third Edition* as a learning resource, not a
purchase prompt. Each Book Guide maps a verified companion file to the concept it teaches, the
relevant library API, and the guide that explains that API. Major task guides link directly to a
matching notebook or case study when one exists. State whether that file calls the library, builds
the method manually for teaching, or illustrates a related workflow. When no relevant public file
exists, omit the link rather than inventing a match.

Book links must be clickable GitHub file URLs at a fixed companion commit. Check each path against
that commit's Git tree and update the map when the book changes. A site should use one documented
companion revision for its book links, so readers do not silently cross incompatible notebook
versions. Explain material differences between book inputs and library examples, including data
availability, package versions, training cost, execution settings, or required services. Link from
the Book Guide back to the relevant library guide. Link from the book to library documentation when
the book repository's own work is next updated; library documentation must be useful on its own.

## Maintained Quantopian libraries and successor guidance

Zipline, Alphalens, and Pyfolio remain useful reference points. Where a task overlaps with the ML4T
stack, give readers a factual migration map: Zipline simulation to Backtest, Alphalens factor
analysis to Diagnostic and, where relevant, Engineer, and Pyfolio performance analysis to
Diagnostic. Name the specific supported task and API on each side, required input conversion, and
material differences. Acknowledge useful behavior that the newer package does not provide. Do not
assert general superiority, complete compatibility, or an end-of-life date without evidence. The
older repositories' maintainers own any future notice in those repositories; the six library sites
can provide the destination guidance now.

## Discovery and review evidence

Use descriptive page titles, one clear heading per page, a factual page summary, stable canonical
URLs, and navigation labels that match readers' tasks. Explain terms people search for in the page
that answers the corresponding task. Avoid repeated keywords, generic comparison claims, or
duplicating the book's teaching text. Keep diagrams, tables, and screenshots legible, with text
alternatives where the visual carries information.

A documentation change is ready for review when its pull request records the capability inventory,
the companion commit used for book links, the examples actually executed, link-check results,
`uv run mkdocs build --strict`, and any externally dependent examples that could not be run. Review
the rendered navigation and representative pages at desktop and narrow widths. After release,
verify the deployed route and release identity using the checks below. Record exceptions as scoped
findings with an owner; a passing build does not close a content or accuracy gap.

## Build and deployment

- MkDocs is the documentation generator.
- `uv run mkdocs build --strict` must pass in pull requests and releases.
- The canonical base URL and website repository are defined in `config/libraries.toml`.
- Each library route is exactly `{documentation_base_url}{library}/`.
- The deployed site must identify the correct library and released version.
- Navigation, internal links, code samples, and API references must resolve.
- A documentation deployment failure blocks release qualification.

The library workflow builds documentation from the release candidate, records its library, version,
and full commit in the rendered site, and transfers an immutable artifact to the configured website
repository. The website deploys that artifact under the library's route without rebuilding it. The
deployment job validates required credentials before changing external state and is protected from
untrusted pull-request code.

Every deployed page provides the release identity as HTML metadata using `ml4t-library`,
`ml4t-version`, and `ml4t-commit` names. The values are the inventory key, public package version,
and full 40-character release commit. This metadata is part of the publication contract and lets the
ecosystem distinguish a current route from a successful response serving stale content.

Production website changes require the separate approval applicable to `ml4t/website`. After
deployment, an automated check fetches the canonical route and verifies the expected library,
version, commit, navigation, assets, internal links, and representative API pages. All seven routes
in the inventory are first-class website content; the website's own inventory and tests must not
describe a smaller set.

The ecosystem index describes the complete workflow. Library content remains in its release
repository and is reviewed with the code it documents.
