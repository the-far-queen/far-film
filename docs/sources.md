# sources — public-domain film corpora

This file lists the public-domain sources far-film draws from for the
`source_id` axis (AGENTS.md Group G, axis 56). Every shot in this repo
must trace back to one of these (or a license-cleared equivalent).

## primary sources

### archive.org — public-domain films + screenplays
- **url:** https://archive.org/details/feature_films
- **license:** varies; filter for "Public Domain" + "pre-1928" or "pre-1929"
- **what we get:** actual film files + raw screenplay scans
- **notes:** most US films pre-1929 are public domain; later US films
  are mostly not. check each item's `rights` field.

### gutenberg drama shelf — pre-1928 plays
- **url:** https://www.gutenberg.org/ebooks/subjects/search/?query=plays
- **license:** pd
- **what we get:** play scripts (Ibsen, Chekhov, Wilde, Shaw, Shakespeare)
- **notes:** usable as `source_id` for shot sequences adapted from plays.

### wikisource — scripts + screenplays
- **url:** https://en.wikisource.org/wiki/Category:Screenplays
- **license:** pd
- **what we get:** transcribed screenplays
- **notes:** small collection; verify authorship dates.

### imsdb — internet movie script database
- **url:** https://imsdb.com/
- **license:** varies; only pd entries usable
- **what we get:** modern screenplays for reference (not source for pd work)
- **notes:** useful for grammar/structure, not as `source_id` for pd gates.

## public-domain check (every shot must pass)

```python
# Every shot in far-film must have a source_id pointing to a public-
# domain source. The gate refuses shots without source_id (reason:
# no_source_id).
```

## how to add a new source

1. Add the entry under "primary sources" or "secondary sources" with
   the url, license, and what we get.
2. Update the gate (if needed) to recognize the new source format.
3. Add a test in `tests/test_shot.py` verifying the gate behavior.

## See also

- [AGENTS.md](../AGENTS.md) — the contract
- [tools/shot.py](../tools/shot.py) — compile + gate