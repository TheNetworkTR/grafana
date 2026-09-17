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

## One mark, every surface

| File | Where it appears |
| --- | --- |
| `grafana_icon.svg` | menu logo, login logo, preloader |
| `fav32.png`, `apple-touch-icon.png` | browser tab, iOS home screen |
| `grafana_mask_icon*.svg` | Safari pinned tab |
| `g8_login_*.svg` | login backdrop, as a watermark |

All of them carry the **square** The Network. mark. The kit also ships a compact
monogram intended for small surfaces, and it is deliberately not used: the
fleet's consoles are meant to read as one brand before they are optimised slot
by slot.

The cost is stated rather than hidden — in the ~32px surfaces (tab icon, menu
logo) a three-line mark is at the edge of legibility. That is a known trade, not
an oversight.

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

The tab and touch icons sit on the kit's own dark rounded ground, which is what
keeps them legible against a light AND a dark browser chrome.
