# Harbor schedule review — Hermes skill tap

An offline schedule-analysis skill for synthetic calendar fixtures. It detects
overlapping timed events and proposes free intervals during explicit working
hours. It never changes calendars, contacts attendees, or accesses the network.

Install through the Hermes skill tap:

```
hermes skills tap add CallistoAma/csci599-a3-hermes-skills
hermes skills install CallistoAma/csci599-a3-hermes-skills/harbor-schedule-review
```

The coursework submission records an immutable commit and a fresh-install
transcript. The included example is entirely fictional. Python 3.10+ with an
IANA timezone database is required; Hermes' managed runtime provides this.

This skill was developed for CSCI599 A3 with Codex assistance. The submitted process
log identifies AI-generated code and the author's verification. Hermes is an
external dependency; no Hermes source is redistributed here.
