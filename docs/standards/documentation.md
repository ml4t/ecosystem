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

Public metadata and prose must not contain configured placeholder identities, fabricated support
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

Production website changes require the separate approval applicable to `ml4t/website`. After
deployment, an automated check fetches the canonical route and verifies the expected library,
version, commit, navigation, assets, internal links, and representative API pages. All seven routes
in the inventory are first-class website content; the website's own inventory and tests must not
describe a smaller set.

The ecosystem index describes the complete workflow. Library content remains in its release
repository and is reviewed with the code it documents.
