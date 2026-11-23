[![make.fun](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/ikun52521-max/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/ikun52521-max/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123)

# The World in One Day — 23 November 2026

Entry for the make.fun bounty **"Sum up 23 November's world news in one image"**
($100 USDC, https://make.fun/bounty/news-image-20261123).

## What it does

`main.py` (Python 3.13, standard library only) draws a newspaper front page
— "THE WORLD IN ONE DAY" — summing up Monday 23 November 2026 and writes it
to `$MAKEFUN_OUTPUT_DIR/entry.png` (1024x1024 PNG, under 1 MiB). It encodes
the PNG by hand (zlib + CRC32) and renders every letter with a small 5x7 dot
font defined in the file. No network, no randomness, no clock: two runs write
byte-identical output.

## The day's news in the image

- **Lead — COP31 collapses:** the UN climate summit in Antalya ends with no
  agreement, the first collapse since 2009 and the longest COP on record;
  the EU rejects a draft that never names fossil fuels.
- **Ukraine:** a Russian drone strike on a building in the Kyiv region leaves
  at least 14 people missing; Zelenskyy presses the US for Patriot missiles.
- **Gulf war:** Houthis claim strikes on a Saudi oil refinery and radar;
  tankers set ablaze in the Strait of Hormuz.
- **Black Sea:** suspected Ukrainian sea drones hit a Russian warship at the
  Benghazi naval base in Libya.
- **Tech:** nations agree at a UN conference to keep negotiating rules for
  lethal autonomous weapons.
- **Asia:** South Korea's education minister resigns amid an AI exam-cheating
  scandal.
- **Sport:** the World Chess Championship opens (Sindarov takes White in
  Game 1) and India posts a record 720 for 9 declared in Wellington.
- **Also today:** Nepal PM Balendra Shah meets Modi in Delhi; thousands
  march in Lisbon over living costs; 50 missing after an Indonesian factory
  fire; Myanmar's junta calls an ASEAN decision unfair; a father and
  daughter are held by ICE at Seattle airport.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

## License

MIT — see [LICENSE](LICENSE).
