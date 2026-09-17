# radaros-brand

The Network. artwork that this branch puts in place of Grafana's own, and the
script that renders it.

## Why the images are committed and the sources are not

`generate.py` takes two arguments: the brand kit's SVG directory and the
path-converted square mark. Neither lives here. The kit is a design asset that
belongs to its owner, not to a fork of Grafana, and this repository is public.
What is committed is the OUTPUT — the files Grafana's own code imports — so the
build needs nothing but this checkout, and a reviewer can see exactly what ships.

The script stays for the question that always comes later: where did these come
from, and how do I make them again.

```bash
./generate.py <brand-kit-svg-dir> <path-converted-square-mark.svg>
```

It writes into `../public/img/`, replacing upstream artwork **by filename**.
That is deliberate: `Branding.tsx` already imports `grafana_icon.svg`,
`g8_login_dark.svg` and `g8_login_light.svg`, so keeping the names means the
patch to that file never has to re-point an import, and a rebase onto a newer
upstream tag stays a text-only conflict at worst.

## Two scales, which is the whole point

The kit ships a compact monogram for small surfaces and a full three-line mark
for large ones. That distinction is not decoration:

| Surface | Size | Gets |
| --- | --- | --- |
| Menu logo, login logo, preloader (`grafana_icon.svg`) | ~32px box | monogram |
| Tab and touch icon (`fav32.png`, `apple-touch-icon.png`) | 32px / 180px | monogram on the kit's dark ground |
| Safari pinned tab (`grafana_mask_icon*.svg`) | 16px | monogram |
| Login backdrop (`g8_login_*.svg`) | 1920×1080 | full mark, held back as a watermark |

Measured before deciding: the full mark rendered into a 32px box is unreadable —
three lines of type collapse into noise. The monogram is legible at the same
size and, being roughly 2:1, also sits correctly in the wide slots.

## Themes

`grafana_icon.svg` carries both colourways in one file, switched by
`@media (prefers-color-scheme: dark)` inside the SVG. That query reads the
**browser's** theme, not Grafana's, so the deployment sets
`GF_USERS_DEFAULT_THEME=system` to tie the two to one source. Without that, a
console pinned to the dark theme in a light-mode browser would show a black mark
on a dark sidebar.

The login backdrops are separate files because Grafana picks between them itself
(`theme.isDark` in `Branding.tsx`), which is the one place upstream already does
the theme switch for us.
