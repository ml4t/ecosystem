# Shared standards

The standards in this section apply to all seven stable libraries. A library may add stricter
requirements but may not weaken a shared requirement locally.

- [Compatibility](compatibility.md)
- [Release qualification](release-qualification.md)
- [Documentation](documentation.md)
- [Issues and pull requests](issues-and-pull-requests.md)
- [API compatibility](api-compatibility.md)
- [Dependencies and security](dependencies-and-security.md)
- [Agent guides](agent-guides.md)

Exceptions must identify their scope, rationale, approver, and an expiration date or objective
review triggers. An expired exception does not qualify a release. A prerelease wait remains valid
until its owning review establishes that the complete dependency set passes the target matrix.
