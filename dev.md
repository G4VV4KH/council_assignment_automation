# council assignment automation — developer notes

The editable publication description is `publishing/description.en.md`. README
and platform descriptions are generated from it. The authoring tree is resolved
through the workspace release registry; the local DEV descriptor is deliberately
prefixed. Distribution removes only that explicit prefix.

## Runtime design

The three ruler variables `caa_enabled`, `caa_prioritize_powerful` and
`caa_observer` store checkbox preferences by their presence. They default off.
The council window adds one button; a separate scripted widget holds the
settings panel. The scheduler and assignment calculation run in game scripts,
independently of panel visibility.

The assignment problem includes the chancellor, steward, marshal, spymaster
and a court chaplain where the ruler has appointment rights. Protected incumbent
chaplains remain fixed, including lifetime appointments. Candidates are distinct.
The optimizer compares complete assignments, retaining required incumbents,
maximizing filled seats, then powerful-vassal representation when enabled,
then the sum of relevant skills, then unchanged incumbent assignments. It has
no arbitrary candidate shortlist or skill ceiling. Protected appointments
remain fixed. With replacements off, ordinary incumbents remain fixed;
serving powerful vassals may exchange eligible positions when priority is on.

Newly enabled automation and policy changes trigger an immediate review. The
saved event chain checks again every 30 game days. Turning automation off stops
new assignments and preserves the other two preferences. The native player
character change hook copies all three preferences, including OFF states, to
the new player character. The previous ruler is no longer automated when AI
controlled. First use without inherited preferences starts off.

## Compatibility

The only vanilla GUI replacement is `gui/window_council.gui`, based on CK3
1.20.0.4. Merge its marked CAA button insertion with other council UI changes
when producing a compatibility patch. The runtime does not depend on a UI
framework or another mod. Nomadic, adventurer and ministry systems are excluded.

Changes to these files require static and isolated native CK3 checks. Include
the open council/settings panel path, a closed-panel interval, the Off path,
skill/powerful selection, globally beneficial cycles, incumbent replacement,
and protected/unsupported position cases. Localization needs engine resolution
in every installed supported language as well as semantic translation review.
Hidden launches do not prove clipping, hover or visual layout.

## Media and publication

The cover was made with built-in imagegen from the author's council icon.
`publishing/media/prompts.txt` records the prompts and
`publishing/media/media-provenance.json` records the source and delivery hashes.
Mechanical resizing produces the square cover, runtime thumbnail and separate
landscape cover. These are promotional artwork, not gameplay screenshots.

Code, localization and publication prose were developed with AI assistance.
No new reuse permission or open-source license is granted here. Platform
identities remain unassigned until actual publication; local preparation never
constitutes an upload or a delivered-byte verification.
