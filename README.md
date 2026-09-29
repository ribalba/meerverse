# meerverse

The meer* universe: the site at [meerverse.com](https://meerverse.com) that
shows the whole family in one place.

| App | What | Site | Source |
| --- | --- | --- | --- |
| meercal | Calendar | [meercal.com](https://meercal.com) | [ribalba/meercal](https://github.com/ribalba/meercal) |
| meerail | Mail | [meerail.com](https://meerail.com) | [ribalba/meerail](https://github.com/ribalba/meerail) |
| meerato | Tasks | [meerato.com](https://meerato.com) | [ribalba/meerato](https://github.com/ribalba/meerato) |
| meerpic | Photos | [meerpic.com](https://meerpic.com) | [ribalba/meerpic](https://github.com/ribalba/meerpic) |
| meerink | Professional network (coming soon) | [meerink.com](https://meerink.com) | [ribalba/meerink](https://github.com/ribalba/meerink) |
| meerpad | Writing (coming soon) | [meerpad.com](https://meerpad.com) | [ribalba/meerpad](https://github.com/ribalba/meerpad) |

A static page, a stylesheet and some images, served by nginx. Nothing to
build.

## Running it locally

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
# http://127.0.0.1:8082
```

The dev overlay publishes the port (8080 and 8081 are meerail's and meercal's
sites, so all three run side by side) and mounts `public/` over the image, so
an edit is a reload away. `WEBSITE_PORT=9000` moves it.

## Deploying on Coolify

`docker-compose.yml` is the Coolify file: one service, `website`, with
`expose` rather than `ports`, since Coolify's Traefik reaches it over the
project network and terminates TLS in front of it.

1. **New resource**, pick this repository, build pack **Docker Compose**,
   compose file `/docker-compose.yml`.
2. On the `website` service set **Domains** to
   `https://meerverse.com,https://www.meerverse.com`. Port 80 is the one
   Coolify routes to when a domain names none. nginx answers the `www` name with
   a 301 to the bare domain, so there is one canonical address.
3. Point the DNS A records for `meerverse.com` and `www.meerverse.com` at the
   Coolify host, and deploy. The image has a healthcheck, so Coolify only
   switches traffic once nginx answers.

Nothing is stored and nothing is secret: the container is disposable, and
there are no environment variables to set.

## The styles

`public/css/site.css` is meercal's `website/public/css/site.css` copied
verbatim, which is itself meerail's, which is meerato's landing page: the sites
are one family and should read as one. Keep everything above the
`===== meerverse additions =====` heading byte-identical to meercal's, so a fix
to one site can be carried to the others with a plain diff:

```bash
diff <(tail -n +7 ../meercal/website/public/css/site.css) \
     <(sed -n '7,/===== meerverse additions/p' public/css/site.css | head -n -2)
```

No output means the shared part is still identical.

The screenshot slider and lightbox scripts at the foot of `index.html` are
meercal's too, copied unchanged.

## Images

Every picture on the page belongs to one of the apps. `tools/build_assets.py`
pulls the logos and screenshots in from sibling checkouts (`../meercal`,
`../meerail`, `../meerato`, `../meeroto`, `../meerink`) and writes WebP into
`public/img/`:

```bash
python3 tools/build_assets.py      # needs Pillow
```

Two of them are stand-ins until meerverse has artwork of its own: the hero
(`img/family.webp`, the four shipping apps' meerkats composed into one group)
and the brand mark and favicons (`img/brand*`, meerato's waving meerkat).

meerpad has no checkout yet, so its logo source is kept here in
`assets/meerpad.png` (trimmed to 512px, with the stray almost-transparent
pixels around the edge cleared). Once a meerpad repo exists, point `LOGOS` in
the script at it and delete the copy.

`public/llms.txt` is the same content in plain text for language models, and
the page carries it again as schema.org data. Keep the three in step.
