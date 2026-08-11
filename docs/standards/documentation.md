# Documentation

Each library owns its user and API documentation. The ecosystem owns the shared publication
requirements and index.

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

## Build and deployment

- MkDocs is the documentation generator.
- `uv run mkdocs build --strict` must pass in pull requests and releases.
- The canonical route is `https://www.ml4trading.io/docs/{library}/`.
- The deployed site must identify the correct library and released version.
- Navigation, internal links, code samples, and API references must resolve.
- A documentation deployment failure blocks release qualification.

The ecosystem index describes the complete workflow. Library content remains in its release
repository and is reviewed with the code it documents.
