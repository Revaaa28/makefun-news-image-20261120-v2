# The World in One Day — Friday 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Revaaa28/makefun-news-image-20261120-v2/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Revaaa28/makefun-news-image-20261120-v2/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A single 1024x1024 PNG that sums up the world news of **Friday 20 November
2026** as a broadsheet newspaper front page: 35 stories across 7 regions,
every one of them dated to that Friday, with a source named beside each
story.

## What's on the page

- A giant serif masthead naming the day, a one-line deck of the top stories,
  and a strip of six big numbers from the day.
- A colour region bar (Europe 8, Asia 8, Middle East 3, Africa 5,
  Americas 4, Oceania 3, Global 4).
- Three illustrated hero stories: the missile barrage that hit Kyiv's three
  Dnipro bridges; Cyclone Akvan coming ashore at Gopalpur in Odisha; and the
  AI sell-off that sank Asia's stock markets at Friday's close.
- Ten illustrated briefs, a drawn world map with numbered pins showing where
  each story happened, and a numbered index of 22 more Friday stories.
- A red "DATE CHECK" box listing the Thursday 19 November stories that were
  deliberately left out (the World Court ruling on Myanmar, the Shenzhen
  three-leader declaration, Tonga's drought emergency, the migrant boat lost
  off Senegal) and the things that had not happened yet (BepiColombo's
  Mercury orbit entry, any final COP31 text).

All illustrations are original flat drawings made in code for this page.

## Files

- `draw.py` — the program that renders the page (Python + Pillow only).
  Deterministic: no randomness, no timestamps; running it twice produces a
  byte-identical `entry.png`.
- `entry.png` — the rendered front page (1024x1024, under 1 MiB).
- `main.py` — the entrypoint. Validates `entry.png` (PNG, exactly
  1024x1024, at most 1 MiB) and copies it to the directory named by the
  `MAKEFUN_OUTPUT_DIR` environment variable (default `/output`).
  Standard library only.
- `SOURCES.md` — every story on the page with the outlet that reported it.

## How to run

```sh
python3 draw.py            # re-render entry.png from source
python3 main.py            # validate and copy entry.png to /output
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py   # ...or to a directory you choose
```

Requires Python 3 and Pillow (for `draw.py` only), plus the DejaVu fonts
(DejaVuSerif-Bold, DejaVuSans, DejaVuSans-Bold).
