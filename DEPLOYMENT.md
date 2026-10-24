# Repository and reader publication

The public collection is maintained in [Faedriel/neomythism](https://github.com/Faedriel/neomythism). Edition 0.8 is dated 24 October 2026. Future additions use new commits that preserve the existing publication history.

The reading site is configured for [faedriel.github.io/neomythism](https://faedriel.github.io/neomythism/). In repository Settings → Pages, select **Deploy from a branch**, **main**, and **/docs**. The ready-made reader is in `docs/`; `docs/index.html` also opens locally. Keep the repository public for discovery.

For a future address under neomythism.net, change `base_url` in catalog.json and rebuild before deploying. Do not upload a CNAME file or change DNS until that destination is selected. Link the existing neomythism.net library and repository in both directions.

The generated pages have ordinary HTML content, descriptive titles, author identities, canonical URLs, and a sitemap. Research landing pages have scholarly citation metadata; only the available Made and Real PDF has a citation_pdf_url. `llms.txt` is an optional reading map, not an indexing or ranking guarantee. No robots.txt is provided for this project path: crawling rules belong at the root of the actual host. Preserve existing site exclusions if deploying under neomythism.net.

After deployment or an update, verify representative pages and PDFs. Sitemap submission through Google Search Console or Bing Webmaster Tools is a separate account-level step. Neither indexing nor AI citation is guaranteed by publication or metadata.

## Rebuild

Install the dependencies listed in `package.json` and `requirements.txt`, then run `python scripts/build_site.py`. The static files already included need no build to read. The build accepts NODE_BIN and MARKED_MODULE environment overrides and does not upload anything.

Implementation references: [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site), [GitHub citation files](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files), [Google Scholar inclusion](https://scholar.google.com/intl/en/scholar/inclusion.html).
