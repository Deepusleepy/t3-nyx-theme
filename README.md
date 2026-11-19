# Nyx

A night-sky theme for [T3 Code](https://t3.codes). The background is a starry sky with a purple aurora, drawn as tiny glowing dots like an LED screen. Menus and panels stay see-through like the default T3 look.

![New thread](previews/new-thread.png)
![A conversation](previews/thread.png)
![Model picker](previews/model-picker.png)
![Side panel](previews/side-panel.png)
![Pull requests](previews/pull-requests.png)
![Usage](previews/usage.png)
![Settings](previews/settings.png)

## Nyx Plus

Nyx Plus is the same sky with two layout changes:

- **Title-first threads.** Each sidebar row shows the thread title on top, then the project and status, then the branch. Pinned and draft markers sit in front of the title.
- **A simpler model picker.** Search on top, then provider icons, the model list, and glass keys for effort. The effort keys slide between levels and hide for models that have none. Fast is one on/off key, like Ultracode, and favorite stars glow lavender.

![Nyx Plus sidebar](previews/plus-sidebar.png)
![Nyx Plus model picker](previews/plus-model-picker.png)

## Install

Install one or both. Nyx changes only colours and the background. Nyx Plus also changes the sidebar rows and the model picker. If you install both, the one you install last is the one T3 uses, and you can switch between them in the theme picker.

```sh
curl -fsSL https://raw.githubusercontent.com/Deepusleepy/t3-nyx-theme/main/nyx.json -o nyx.json
t3 theme set nyx.json
```

```sh
curl -fsSL https://raw.githubusercontent.com/Deepusleepy/t3-nyx-theme/main/nyx-plus.json -o nyx-plus.json
t3 theme set nyx-plus.json
```

T3 switches right away, in the desktop app and in the browser. To go back, pick another theme in the theme picker or run `t3 theme set t3-chat`.

### Let your agent install it

Paste this into a T3 Code thread:

> Install a theme from https://github.com/Deepusleepy/t3-nyx-theme. Follow the "Instructions for agents" section of its README.

Your agent will ask whether you want Nyx, Nyx Plus or both. To skip the question, name your pick in the message.

### Instructions for agents

1. This repo has two themes. **Nyx** changes only colours and the background. **Nyx Plus** is the same sky plus title-first sidebar rows and a simpler model picker. Both can be installed side by side.
2. Unless the user already said "Nyx Plus", "plain Nyx" or "both", ask which they want: Nyx, Nyx Plus, or both. "The Nyx theme" alone is not a choice, so ask. If they want both, also ask which one to use now.
3. Download each chosen file: `https://raw.githubusercontent.com/Deepusleepy/t3-nyx-theme/main/nyx.json` and/or `https://raw.githubusercontent.com/Deepusleepy/t3-nyx-theme/main/nyx-plus.json`.
4. If the `t3` command is available, run `t3 theme set <path to the file>` for each file. Otherwise call the `t3_theme_set` tool for each, with `themeId` set to `"nyx"` or `"nyx-plus"` and the file's JSON as `theme`.
5. Each install also switches T3 to that theme, so install the one the user wants to use now last. Both stay in the theme picker.
6. Do not edit the files. They are close to the size limit T3 allows for themes.

## Requirements

- A recent T3 Code Nightly (November 2026 or later).
- Works in the desktop app and the browser. The phone app doesn't use themes.

## Notes

- Nyx is dark only. It keeps T3 dark even when your computer is in light mode.
- The see-through look follows the Glass opacity slider in Settings › Appearance. It looks best at around 40%, which is what the screenshots use.
- The sky fills the window at any size.
- If a future T3 update changes its layout, a few small touches may fall back to T3's normal look. Nothing breaks.

## Change the theme yourself

`theme.css` holds the shared styles and `plus.css` adds the Nyx Plus layout. `art.py` draws the sky, and `build.py` puts them together into `nyx.json` and `nyx-plus.json`.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build.py
```

## License

[MIT](LICENSE)
