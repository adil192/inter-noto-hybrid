# Inter Noto Sans Hybrid

This project intends to use Noto Sans to supplement Inter's language support.
Inter only supports Cyrillic, Greek, and Latin scripts, so languages like Arabic, Armenian, Hindi, Thai, etc. can't be displayed with Inter alone.

I needed a singular merged font for my package
[`golden_screenshot`](https://github.com/adil192/golden_screenshot) since
Flutter's test environment cannot use font fallbacks.
These merged fonts are replacing the original Inter font and should look
almost exactly the same except with non-Cyrillic/Greek/Latin scripts,
where real glyphs can be used.

If you are looking for an official Noto release or official Inter release,
you've found the wrong repo.
Most people should not use these merged fonts, and should instead install Inter
and Noto fonts separately. The vast majority of apps and browsers support font
fallbacks so a merged font is not usually needed.

The main script ([`megamerge/megamerge.py`](megamerge/megamerge.py)) is based
on the script of the same name from the original
[notofonts](https://github.com/notofonts/notofonts.github.io) repo,
but heavily modified to use Inter as the base font and to fix certain
conflicts.

You can find the merged fonts inside the `megamerge/` directory.

## Licensing

All Noto fonts (in the `fonts/` and `megamerge/` directories) are licensed under the [SIL Open Font License](fonts/LICENSE).

This documentation and all tooling in this repository is licensed under the [Apache 2.0 License](LICENSE).

## Screenshot

Here is Inter vs InterNotoSansHybrid:

<img width="1114" height="1260" src="https://github.com/user-attachments/assets/a87bb798-6840-4001-9c01-c96195076038" />
