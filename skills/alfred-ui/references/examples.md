# Alfred UI examples

Real, public Alfred UI workflows (checked 2026-11-20), grouped by the pattern they show. Find the closest interaction pattern and open its `ui.json` for API usage. Adapt the structure to the requested workflow; example-specific data, styling and architecture are not requirements. alfredapp/* repos are first-party and the most reliable. Third-party repos contain some mistakes, listed under Known mistakes.

Contents:
- [Pick by pattern](#pick-by-pattern)
- [Idioms seen across repos](#idioms-seen-across-repos)
- [Web page idioms](#web-page-idioms)
- [Design notes](#design-notes)
- [Known mistakes in examples](#known-mistakes-in-examples)
- [Official docs](#official-docs)

## Pick by pattern

| Pattern | Example | Read it for |
|---|---|---|
| **Searchable list or grid that returns a pick** | [sf-symbols-browser ui.json](https://github.com/alfredapp/sf-symbols-browser-workflow/blob/main/Workflow/symbolsbrowser.alfredui/ui.json) + [components/](https://github.com/alfredapp/sf-symbols-browser-workflow/tree/main/Workflow/symbolsbrowser.alfredui/components) | Script-free: a dataview grid with `{fileraw:}` data, a filter, arrow-key shortcuts, a detail panel updated from the selection, and `finish` to Copy to Clipboard |
| **List + detail pane, actions on the selection** | [text-transformer ui.json](https://github.com/alfredapp/text-transformer-workflow/blob/main/Workflow/text-transformer.alfredui/ui.json) | Flex layout with column weights, a filterable dataview, a script updating the output pane on `changed`, a ⌘-shortcut `finish` with variables, then a Conditional |
| **Live list fed by a program** | [browvitab ui.json](https://github.com/chmouel/alfred-browvitab/blob/main/workflow/tabs.alfredui/ui.json) + [tablist.json](https://github.com/chmouel/alfred-browvitab/blob/main/workflow/tabs.alfredui/components/tablist.json) | Data replaced through `update` + `data.select`, a fingerprinted `pulse`, row context menus with `{data:}`, a popup menu, actions in `actions/*.json`, `finish` + Run Script |
| **Icon grid with templates and persisted state** | [launchpad ui.json](https://github.com/alfredapp/launchpad-workflow/blob/main/Workflow/launchpad.alfredui/ui.json) | `templates` + `{param:}`, a script that rebuilds a grid with `update … components`, `persist` state, `fileicon` images |
| **Form → result** | [no-bs-yt ui.json](https://github.com/alfredapp/no-bs-yt-workflow/blob/main/Workflow/nobsyt.alfredui/ui.json) + [get-channel](https://github.com/alfredapp/no-bs-yt-workflow/blob/main/Workflow/nobsyt.alfredui/get-channel) | Form layout, pickers with persisted choices, "Working…" feedback before a script, a button with `shortcut: "↩"`, `finish` to Copy |
| **Form with a web preview, swapping the view** | [hackerboard ui.json](https://github.com/vitorgalvao/hackerboard-workflow/blob/main/Workflow/submit.alfredui/ui.json) | Two args via a Split utility, `webkitview` `src` updated on `typingstopped`, `replace` swapping the whole view |
| **Web page + hand-back buttons** | [alfred-gallery browser.alfredui](https://github.com/alfredapp/alfred-gallery-workflow/blob/main/Workflow/browser.alfredui/ui.json) | `webkitview` with an `openlinksexternally` regex, `{value:webview.src}` through action `variables` into `finish.variables`, a Conditional routing navigate or install |
| **Device-sized web preview** | [mobile-web-tester ui.json](https://github.com/alfredapp/mobile-web-tester-workflow/blob/main/Workflow/tester.alfredui/ui.json) | `webkitview` sized at run time through `constraints.size`, `window.resize`, a picker built from user config, launch mode from user config |
| **Async fetch → Markdown answer** | [alfredq ui.json](https://github.com/aboustayyef/alfredq/blob/main/answer.alfredui/ui.json) + [ask.js](https://github.com/aboustayyef/alfredq/blob/main/answer.alfredui/ask.js) | `preload` async script, `markdownarea`, the window resized to the content, copy through action `variables`, user-config API key |
| **Streaming chat** | [brain-outsourcing ui.json](https://github.com/alfredapp/brain-outsourcing-workflow/blob/main/Workflow/chatwindow.alfredui/ui.json) | `pulse` streaming loop, `markdownarea` `append`/`replacelast`, action arrays stored in `variables`, event `confirm`, `data.modify` insert and delete |
| **Chat with attachments and presets** | [alfred-claude-chat ui.json](https://github.com/mikomagni/alfred-claude-chat/blob/main/Workflow/chatwindow.alfredui/ui.json) | `opendialog`, `sheet`, an inbox read by the pulse (input from other processes), one bundle behind two UI objects |
| **Fully styled HTML view** | [stupid-questions ui.json](https://github.com/johnbeeler/alfred-stupid-questions/blob/main/src/answer.alfredui/ui.json) | `webkitview` `text` built from HTML and CSS by scripts, for full visual control |
| **Dashboard built by a script** | [ai-usage-dashboard ui.json](https://github.com/rymawby/alfred-6-ui-ai-usage-dashboard/blob/main/workflow/claude-usage.alfredui/ui.json) + [scripts/dashboard](https://github.com/rymawby/alfred-6-ui-ai-usage-dashboard/blob/main/workflow/claude-usage.alfredui/scripts/dashboard) | A shell `ui.json` filled by one `update … components`, KPI cards and charts from views and `progress`, refresh by pulse, ⎋ and ⌘W close |
| **Floating live window** | [timers ui.json](https://github.com/alfredapp/timers-workflow/blob/main/Workflow/timers.alfredui/ui.json) | 1-second pulse, round `progress` in cells, sheets, notifications, named `colours`, `alfred_ui_source` |
| **Job progress / status** | [clip-upload status.alfredui](https://github.com/MuhametSmaili/dotfiles/blob/main/.config/alfred/workflows/clip-upload/status.alfredui/ui.json) · [rime-updater](https://github.com/BlackCCCat/Alfred-Workflow/blob/main/rime-updater/alfred6/wanxiang.alfredui/ui.json) | `launched` async job → update, a polling pulse that switches itself off when idle, a linear `progress` |
| **Image preview + confirm** | [clip-upload shot.alfredui](https://github.com/MuhametSmaili/dotfiles/blob/main/.config/alfred/workflows/clip-upload/shot.alfredui/ui.json) | `imageview` set by a script, cleanup on `quit` |
| **Confirm / error dialog** | [rex confirm-rebuild](https://github.com/ryan-token/alfred-rex-workspaces/blob/main/ui/confirm-rebuild.alfredui/ui.json) · [rex error](https://github.com/ryan-token/alfred-rex-workspaces/blob/main/ui/error.alfredui/ui.json) · [info.plist](https://github.com/ryan-token/alfred-rex-workspaces/blob/main/info.plist) | Script-free alert layout (symbol, text, buttons), `finish` variables to a Conditional, bundles kept in `ui/` |
| **Live JSON playground** | [try-alfred-ui ui.json](https://github.com/alfredapp/try-alfred-ui-workflow/blob/main/Workflow/try.alfredui/ui.json) + [scripts/render](https://github.com/alfredapp/try-alfred-ui-workflow/blob/main/Workflow/try.alfredui/scripts/render) | Injecting any component tree at run time, `events` from a `{file:}`, saving on `quit` |
| **Generating bundles from code** | [alfred-go ui.go](https://github.com/Brookke/alfred-go/blob/main/ui.go) · [rime build_workflow.py](https://github.com/BlackCCCat/Alfred-Workflow/blob/main/rime-updater/alfred6/build_workflow.py) · [browvitab build.py](https://github.com/chmouel/alfred-browvitab/blob/main/scripts/build.py) | Writing `info.plist` and the bundle programmatically, and migrating an Alfred 5 Text View object to Alfred UI |

To read a raw file, swap `github.com/<repo>/blob/` for `raw.githubusercontent.com/<repo>/`, or run `gh api repos/<repo>/contents/<path> --jq .content | base64 -d`.

## Idioms seen across repos

- **Dataview row styling.** `cell.init` resets a reused cell. `cell.selected` styles the selection, almost always with `alfredSelectedResultBackgroundColor` and `alfredSelectedResultTextColor`. Both are maps of `"<cellId>.<prop>": value`.
- **Detail pane from the selection, without a script.** On the dataview's `changed` event, run a `json` action whose `variables` read `{value:self.selected.<cellId>.<prop>}`, then `update` the detail components with `{var:}` (sf-symbols).
- **Feedback first.** An action array starts with a `json` `update` (a "Loading…" label, a disabled button, a visible `progress`), then runs the async script.
- **Reusable actions.** Keep an action array in top-level `variables` and reference it as `"action": "{var:name}"`, or keep it in `actions/x.json` and reference it as `"action": "{file:actions/x.json}"`.
- **Clicks and keys run the same action.** Point a button's `actioned` event and a root `shortcuts` entry at one stored action.
- **Hidden row values.** Put what an action needs but the row doesn't show (a URL, an id) in a plain key such as `"url"` and read it with `{value:<dataviewId>.selected.url}` or `{data:url}`.
- **Images in cells.** `"thumb.image": {"type": "file", "src": "/abs/path.png"}`. Use `fileicon` for an app or file icon, and `symbol` for an SF Symbol fallback. No IMAGE type is documented to take a URL: download remote images to `alfred_workflow_cache` and pass the path. `contenttintcolour` tints symbols only, so a `file` image on a selectable row needs colours that read on both the normal and the selected background, such as a mid-grey glyph.
- **Window sized to content.** A script returns `{"window":{"resize":{"height":N}}}`; use `"auto"` to fit.
- **Several exits:** `finish` + `variables` + a Conditional (see `workflow.md` §5).
- **Events style.** A single event object and an event without `triggers` are valid (since Build 3145; `triggers` defaults to `actioned`). An array with explicit `triggers` reads better and is easier to extend.

## Web page idioms

Choose how to present web content according to the task:

- **Browse a URL.** Set `webkitview.src`; use the view's `back`, `forward` and `reload` functions when navigation controls are needed. The official Gallery browser is an example.
- **Render generated content.** Set `webkitview.text` for HTML produced by a script, or load a local HTML file with `src`. Use this when native components do not fit the content.
- **Test a viewport.** Set `constraints.size` and resize the window to suit the requested viewport, as in the official Mobile Web Tester. Do not assume every web view needs a desktop-sized page or a wrapper iframe.

`changed` reports navigation starting, not loading finishing. If you control the HTML, handle DOM load events within that page. Do not assume a remote page can be embedded: its framing policy may forbid it.

## Design notes

These are choices to make for the task, not a required window design:

- A picker may need only a searchable list; a form may need no list at all. Use a detail pane when selected items need additional context.
- Choose row content, labels and visible states around the user's actions. A compact picker may omit normal states; a monitoring dashboard may need to show them explicitly.
- Native components suit standard controls; a web view can suit custom content. Keep the user's requested interaction and appearance rather than copying an example's design.

## Known mistakes in examples

Don't copy these:

- `"color"` (hackerboard, one place in no-bs-yt): the key is `colour`.
- `copy.type: "string"` (launchpad): use `"text"`, `"file"` or `"url"`.
- `{"closeonescape": true}` as a JSON action (stupid-questions): `closeonescape` is a `sheet` key, not a command.
- Raw key codes in shortcuts: use glyphs such as `"↓"`, `"⎋"`, `"⌘↩"`.

## Official docs

- Alfred UI index: https://www.alfredapp.com/help/alfredui/ (components, layouts, actions, JSON actions, placeholders, variables, pulse, log)
- Tutorials (each has a downloadable workflow): https://www.alfredapp.com/help/alfredui/tutorials/ covering Sound Board (grid, templates), Speak the Text (border, focus), Text to Markdown (`{file:}` modules), Web Browser (external window, webkitview, `args[0]`) and Colour Search (dataview, filter, `finish`)
- Workflow object: https://www.alfredapp.com/help/workflows/user-interface/alfredui/
- Changelog (schema changes during the beta): https://www.alfredapp.com/changelog/
