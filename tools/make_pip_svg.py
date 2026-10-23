"""Builds the GitHub profile's Pip graphics from mob-util-app's own sprite data.

  pip-field.svg  - Pip in his field (day sky, sun, drifting clouds, an oak, grass): he stands,
                   blinks, sometimes looks the other way, and walks off to a random spot, like
                   the app's PipRoom/PipBrain. A 48 s timeline that loops seamlessly.
  pip.svg        - Pip standing (idle frame), small, for inline use.

Copied from mob-util-app (keep in sync by hand if Pip changes):
  lib/widgets/pip_sprites.dart  PipSprites._head/_legs/_face, tree, cloud shapes
  lib/core/theme.dart           PipColours
  lib/core/pip_brain.dart       speed 14 px/s, stepTime 0.14 s, 1 px bob on step1/step3, stand 1.5-5 s, blink 0.15 s
                                every 2-5 s, 40% chance to turn while standing, walk >= 6 px
  lib/widgets/pip_room.dart     sky bands + dithered edges, sun, clouds, grass/dirt pattern
Run: python3 tools/make_pip_svg.py   (writes both files to the repo root)
"""
import os
import random

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root

# --- Pip -------------------------------------------------------------------
HEAD = (['.........A..........', '.........L..........', '...LLLLLLLLLLLLLL...', '..LLLLLLLLLLLLLLLL..']
        + ['..LWWWWWWWWWWWWWWL..'] * 9 + ['..LLLLLLLLLLLLLLLL..', '...OOOOOOOOOOOOOO...', '...SSSSSSSSSSSSSS...'])
LEGS = {
    'stand': ['.....OO......OO.....', '.....OO......OO.....', '.....SS......SS.....'],
    'stepL': ['.....OO......OO.....', '.....SS......OO.....', '.............SS.....'],
    'stepR': ['.....OO......OO.....', '.....OO......SS.....', '.....SS.............'],
}
PIP_COL = {'L': '#D97757', 'O': '#C96442', 'S': '#A84F33', 'W': '#F5F0E8', 'K': '#141413', 'A': '#F2C07A'}
PIP_W, PIP_H = 20, 19


def face(kind, look):
    eyes, mouth = [3 + look, 10 + look], 4 + look
    pts = set()
    for e in eyes:
        pts |= {(e, 3), (e + 1, 3)} if kind == 'blink' else {(e, 2), (e + 1, 2), (e, 3), (e + 1, 3)}
    pts |= {(mouth, 5), (mouth + 5, 5)} | {(mouth + i, 6) for i in range(1, 5)}
    return pts


def pip_frame(kind, legs, look=0):
    rows = [list(r) for r in HEAD]
    for x, y in face(kind, look):
        rows[4 + y][3 + x] = 'K'
    return [''.join(r) for r in rows] + LEGS[legs]


# --- His field -------------------------------------------------------------
TREE = [
    '...........H.......B..........', '........HHHHHHHHHHHHHHL.......', '.......HHHHBLHLHHHHHLBLH......',
    '......HHHHHLBLLHHHHLLLHLB.....', '......HBHLLHBLLHHLLLLBLLL.....', '......HHLLHLLLLHLLLLHLLLL.....',
    '.....HLLLHLLLLHLLLLHLLBLDD....', '......LLHLLLLDBLLLDLLLLDD.....', '....HHHBLLLLDLLLLHLLLLDDHLL...',
    '...HHHHHHLLHLLLLHLLLDDHLLLHL..', '...HHHHLLLHLLLLHLLBLHLLLLHLL..', '..HHHHLLBHLLLLDBLLLDLLLBHLLLL.',
    '..BHLLLLHLLLLDLLLLDLLLLHLLLLD.', '..HLLLLHLLLLDLLLLDBBBLHLLLLDD.', '..BLBLHLLBLDLLLBHLLLLDLLLLDDD.',
    '.HHBHHLLLBDDLLLHLLLLDLLLLHLLLL', '.HHLHLLLLDDLLLHLLLLDLLLLHLBLLD', '.LLHLLLLDDDLLHLLLLDLLLDBLLLLDL',
    '.LHLLLLDDDBLDLLLLDLDDDHLBLLDDD', '.HLLLLDDDDLDLLLLDDDDDDLLLLDDDD', '..LLLDDDD.DLLLLDDDDDD.LLLDDDD.',
    '...DDDDD...LLLDDDDDD...DDDDD..', '............DDDDDDD...........',
] + ['.............TTTU.............'] * 13
TREE[23] = '.............TTDU.............'
TREE_CROWN = 23
TREE_COL = {'L': '#4F8E35', 'H': '#8CC65A', 'D': '#356A26', 'B': '#356A26', 'T': '#6E4A2E', 'U': '#4F3420'}
CLOUDS = [
    ['...lll.....', '..lcccll...', '.lcccccclll', 'cccccccccccc', '.ssssssssss.'],
    ['......ll.......', '....llcccl.ll..', '..llcccccccccl.', '.cccccccccccccc', 'ccccccccccccccc', '.sssssssssssss.'],
    ['..ll...', '.lccll.', 'cccccc.', '.ssss..'],
]
CLOUD_COL = {'l': '#FFFFFF', 'c': '#F2F4F8', 's': '#C9D7E8'}
DAY_STOPS = ['#3F78C0', '#5590D0', '#79AEDF', '#A2CBEC', '#C6E2F2', '#DDEFF5']
SUN, SUN_CORE = '#FFD36E', '#FFF0B8'
GRASS, GRASS_LIGHT, DIRT, DIRT_DARK = '#5E8C3A', '#86B85A', '#6B4423', '#4E301A'

COLS, ROWS, PX = 200, 56, 4  # Pip small in a wide field, like Pip Home (Nikola prefers this)
GROUND = 5
GROUND_TOP = ROWS - GROUND


def hexrgb(h):
    return [int(h[i:i + 2], 16) for i in (1, 3, 5)]


def lerp(a, b, t):
    a, b = hexrgb(a), hexrgb(b)
    return '#' + ''.join(f'{round(x + (y - x) * t):02X}' for x, y in zip(a, b))


def runs(cells):
    """cells: dict (x, y) -> colour. Merges horizontal runs into rects."""
    out = []
    for y in sorted({y for _, y in cells}):
        xs = sorted(x for x, yy in cells if yy == y)
        i = 0
        while i < len(xs):
            x, c, n = xs[i], cells[(xs[i], y)], 1
            while i + n < len(xs) and xs[i + n] == x + n and cells[(x + n, y)] == c:
                n += 1
            out.append(f'<rect x="{x * PX}" y="{y * PX}" width="{n * PX}" height="{PX}" fill="{c}"/>')
            i += n
    return ''.join(out)


def sprite(rows, colours, left=0, top=0):
    return {(left + x, top + y): colours[ch] for y, r in enumerate(rows) for x, ch in enumerate(r) if ch in colours}


def sky():
    """Cells, plus the dithered band edges as (row, first x, colour) for a 2-pixel pattern."""
    cells, edges = {}, []
    def colour_at(p):
        f = min(max(p, 0), 1) * (len(DAY_STOPS) - 1)
        i = min(int(f), len(DAY_STOPS) - 2)
        return lerp(DAY_STOPS[i], DAY_STOPS[i + 1], f - i)
    bands = min(max(round(GROUND_TOP / 4), 8), 28)
    band = GROUND_TOP / bands
    for i in range(bands):
        top, bottom = int(i * band), int((i + 1) * band)
        col = colour_at(i / (bands - 1))
        for y in range(top, bottom):
            for x in range(COLS):
                cells[(x, y)] = col
        if i > 0:
            edges.append((top - 1, i % 2, col))
    # The sun, high on the right (PipRoom, the tall "home" size).
    bx, by, br = COLS - 16, 11, 6
    behind = colour_at(by / GROUND_TOP)
    def disc(cx, cy, r, col):
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                if x * x + y * y <= r * r + r:
                    cells[(cx + x, cy + y)] = col
    disc(bx, by, br + 2, lerp(behind, SUN, 0.35))
    disc(bx, by, br - 1, SUN)
    ray = br + 1
    for ox, oy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        for k in range(3):
            cells[(bx + ox * (ray + k), by + oy * (ray + k))] = SUN
    d = round(ray * 0.75)
    for ox, oy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        cells[(bx + ox * d, by + oy * d)] = SUN
        cells[(bx + ox * (d + 1), by + oy * (d + 1))] = SUN
    disc(bx - 1, by - 1, -(-br // 3), SUN_CORE)
    return cells, edges


def clouds():
    """One strip, `wide` pixels, drawn twice so it can scroll left forever."""
    wide = COLS + 24
    spots = [(0.08, 0.18), (0.36, 0.08), (0.55, 0.3), (0.78, 0.45), (0.2, 0.5)]
    cells = {}
    for i, (cx, cy) in enumerate(spots):
        for copy in (0, wide):
            cells.update(sprite(CLOUDS[i % 3], CLOUD_COL, int(COLS * cx) - 12 + copy, int(GROUND_TOP * cy)))
    return cells, wide


def ground():
    cells = {}
    for x in range(COLS):
        cells[(x, GROUND_TOP)] = GRASS
        if (x * 7919) % 13 < 3:
            cells[(x, GROUND_TOP - 1)] = GRASS_LIGHT
        for y in range(1, GROUND):
            cells[(x, GROUND_TOP + y)] = DIRT_DARK if (x * 31 + y * 17) % 11 == 0 else DIRT
    return cells


# --- His day: a timeline like PipBrain's ---------------------------------------
SPEED, STEP_TIME, LOOP = 14.0, 0.14, 48.0


def timeline(seed=7):
    """Segments (t0, t1, kind, x0, x1, facing_right); kind is stand/blink/walk."""
    rng = random.Random(seed)
    start_x, max_x = 92, COLS - PIP_W
    x, right, t, blink_in = start_x, True, 0.0, 2.0
    segs = []

    def stand(dur):
        nonlocal t, right, blink_in
        turn_at = dur * (0.3 + 0.4 * rng.random()) if rng.random() < 0.4 else None
        end, now = t + dur, t
        while now < end:
            nxt = min(end, now + blink_in, t + turn_at if turn_at is not None and t + turn_at > now else end)
            segs.append((now, nxt, 'stand', x, x, right))
            blink_in -= nxt - now
            now = nxt
            if turn_at is not None and abs(now - (t + turn_at)) < 1e-9:
                right = not right
                turn_at = None
            if blink_in <= 1e-9 and now < end:
                b = min(end, now + 0.15)
                segs.append((now, b, 'blink', x, x, right))
                now, blink_in = b, 2 + rng.random() * 3
        t = end

    def walk(target):
        nonlocal t, x, right
        right = target > x
        dur = abs(target - x) / SPEED
        segs.append((t, t + dur, 'walk', x, target, right))
        t, x = t + dur, target

    while True:
        stand(1.5 + rng.random() * 3.5)
        if t > LOOP - 12:
            break
        target = x
        while abs(target - x) < 6:
            target = rng.randint(0, max_x)
        walk(target)
    walk(start_x) if x != start_x else None
    stand(max(1.5, LOOP - t))  # ends where it started, facing right
    if not segs[-1][5]:
        segs.append((segs[-1][1], segs[-1][1] + 0.01, 'stand', start_x, start_x, True))
    return segs


def pct(t, total):
    return f'{100 * t / total:.4f}%'


def field_svg():
    segs = timeline()
    total = segs[-1][1]
    top = GROUND_TOP - PIP_H  # feet on the grass, like PipRoom (bottom = groundTop)
    # Position: held while standing, whole-pixel steps while walking.
    pos = []
    for t0, t1, kind, x0, x1, _ in segs:
        fn = f'steps({max(1, abs(x1 - x0))},end)' if kind == 'walk' else 'step-end'
        pos.append(f'{pct(t0, total)}{{transform:translate({x0 * PX}px,{top * PX}px);animation-timing-function:{fn}}}')
    pos.append(f'100%{{transform:translate({segs[-1][4] * PX}px,{top * PX}px)}}')
    flip = [f'{pct(t0, total)}{{transform:{"none" if r else f"translate({PIP_W * PX}px,0) scale(-1,1)"}}}' for t0, _, _, _, _, r in segs]
    def show(which):
        return [f'{pct(t0, total)}{{opacity:{1 if k == which else 0}}}' for t0, _, k, _, _, _ in segs]
    walk_frames = [pip_frame('smile', 'stepL', 1), pip_frame('smile', 'stand', 1),
                   pip_frame('smile', 'stepR', 1), pip_frame('smile', 'stand', 1)]
    cycle = STEP_TIME * 4
    walk_groups = ''.join(
        # PipBrain.lift: a pixel up on the leg-up steps (step1, step3), the walk's bob.
        f'<g class="wf" style="animation-delay:{-cycle + i * STEP_TIME:.2f}s"'
        f'{f' transform="translate(0,{-PX})"' if i % 2 == 0 else ''}>{runs(sprite(f, PIP_COL))}</g>'
        for i, f in enumerate(walk_frames))
    cloud_cells, wide = clouds()
    tree_x = int(COLS * 0.2)
    crown = sprite(TREE[:TREE_CROWN], TREE_COL, tree_x, GROUND_TOP - len(TREE))
    trunk = sprite(TREE[TREE_CROWN:], TREE_COL, tree_x, GROUND_TOP - len(TREE) + TREE_CROWN)
    W, H = COLS * PX, ROWS * PX
    sky_cells, edges = sky()
    band_colours = {c for _, _, c in edges} | {sky_cells[(0, 0)]}
    sun = {k: v for k, v in sky_cells.items() if v not in band_colours}
    defs = ''.join(
        f'<pattern id="d{i}" width="{2 * PX}" height="{PX}" patternUnits="userSpaceOnUse" x="{off * PX}">'
        f'<rect width="{PX}" height="{PX}" fill="{col}"/></pattern>' for i, (_, off, col) in enumerate(edges))
    dither = ''.join(f'<rect y="{y * PX}" width="{W}" height="{PX}" fill="url(#d{i})"/>' for i, (y, _, _) in enumerate(edges))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" shape-rendering="crispEdges" role="img" aria-label="Pip, a pixel robot, walking around his field">
<style>
.pos{{animation:pos {total:.2f}s step-end infinite}}
.flip{{animation:flip {total:.2f}s step-end infinite}}
.idle{{animation:idle {total:.2f}s step-end infinite}}
.blink{{animation:blink {total:.2f}s step-end infinite}}
.walk{{animation:walk {total:.2f}s step-end infinite}}
.wf{{opacity:0;animation:wf {cycle:.2f}s step-end infinite}}
.clouds{{animation:clouds 160s linear infinite}}
.crown{{animation:sway 3s step-end infinite}}
@keyframes pos{{{''.join(pos)}}}
@keyframes flip{{{''.join(flip)}}}
@keyframes idle{{{''.join(show('stand'))}}}
@keyframes blink{{{''.join(show('blink'))}}}
@keyframes walk{{{''.join(show('walk'))}}}
@keyframes wf{{0%{{opacity:1}}25%{{opacity:0}}}}
@keyframes clouds{{from{{transform:translateX(0)}}to{{transform:translateX(-{wide * PX}px)}}}}
@keyframes sway{{0%{{transform:none}}50%{{transform:translateX({PX}px)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.idle{{opacity:1}}.blink,.walk{{opacity:0}}.pos{{transform:translate({segs[0][3] * PX}px,{top * PX}px)}}}}
</style>
<defs>{defs}</defs>
<g>{runs({k: v for k, v in sky_cells.items() if k not in sun})}{dither}{runs(sun)}</g>
<g class="clouds">{runs(cloud_cells)}</g>
<g class="crown">{runs(crown)}</g>
<g>{runs(trunk)}</g>
<g>{runs(ground())}</g>
<g class="pos"><g class="flip">
<g class="idle">{runs(sprite(pip_frame('smile', 'stand'), PIP_COL))}</g>
<g class="blink" style="opacity:0">{runs(sprite(pip_frame('blink', 'stand'), PIP_COL))}</g>
<g class="walk" style="opacity:0">{walk_groups}</g>
</g></g>
</svg>
'''


def pip_svg(px=3):
    rows = pip_frame('smile', 'stand')
    w, h = PIP_W * px, len(rows) * px
    global PX
    old, PX = PX, px
    body = runs(sprite(rows, PIP_COL))
    PX = old
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'shape-rendering="crispEdges" role="img" aria-label="Pip">{body}</svg>\n')


if __name__ == '__main__':
    with open(os.path.join(HERE, 'pip-field.svg'), 'w') as f:
        f.write(field_svg())
    with open(os.path.join(HERE, 'pip.svg'), 'w') as f:
        f.write(pip_svg())
