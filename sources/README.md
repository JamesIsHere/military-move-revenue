# Sources

Raw authoritative artifacts will be stored immutably beneath this directory after
`goal.md` is ratified. Each artifact must have a matching manifest entry containing
its canonical URL, retrieval timestamp, cryptographic checksum, issuer, version,
effective period, supersession relationship, authority class, and extraction
status.

Do not place real shipment files here. Authorized sanitized historical fixtures
will use a separately controlled intake process and directory.

An unchanged public adjudicative artifact may retain identifiers that appear in
the official publication, but only in the raw archive and archival metadata.
Fixture-facing derivatives must remove those identifiers, carry their own hash,
and link back to the raw artifact checksum.
