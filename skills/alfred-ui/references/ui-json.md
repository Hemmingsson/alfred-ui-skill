# Alfred UI: bundle, ui.json, placeholders, variables and actions

How a `.alfredui` bundle is laid out, what goes at the top of `ui.json`, how values flow in and out, and every action and JSON command. Facts come from the Alfred UI docs (https://www.alfredapp.com/help/alfredui/), the changelog and the first-party example workflows; the wording and examples are this skill's own. **From example** marks facts seen only in working workflows; **Inferred** marks facts reasoned out.

Contents:
- [1. The bundle](#1-the-bundle)
- [2. Top-level keys](#2-top-level-keys)
- [3. Placeholders](#3-placeholders)
- [4. Variables](#4-variables)
- [5. Actions](#5-actions)
- [6. JSON commands](#6-json-commands)
- [7. Getting data in and out](#7-getting-data-in-and-out)
- [8. Pulse](#8-pulse)
- [9. Logging and debugging](#9-logging-and-debugging)
- [10. Ranges at a glance](#10-ranges-at-a-glance)
- [11. Easy to get wrong](#11-easy-to-get-wrong)
- [12. Version history](#12-version-history)

## 1. The bundle

The only fixed rule: a folder whose name ends in `.alfredui`, holding a file called `ui.json`. Everything else is your choice. A typical bundle:

```
notes.alfredui
├─ ui.json
├─ components/   JSON fragments pulled in with {file:}
├─ actions/      reusable action arrays
├─ scripts/      executables run by actions and the pulse
└─ resources/    images, row data
```

- Every path used inside the UI (script `src`, `{file:}`, template files, images, sounds, markdown `src`) is relative to the bundle folder. `{file:}` also takes absolute paths (Build 3184).
- The bundle normally sits in the workflow folder beside `info.plist`, and the workflow object's `path` names it (`workflow.md` §2). A path may step out of the bundle, e.g. `"iconpath": "../icon.png"` for the workflow icon (**From example**).
- Pressing `+` on the workflow object creates a bundle from Alfred's starter template; writing the folder by hand works just as well.
- Scripts are executed directly: give each a shebang and the executable bit. An extension is optional (**From example**).

## 2. Top-level keys

| Key | Type | Notes |
|---|---|---|
| `window` | OBJECT | **Required.** Window settings; `window.root` is the component tree (a `view` is the usual root). |
| `bundleid` | STRING | Recommended; **required for `persist`**. Not preprocessed. |
| `variables` | OBJECT | Starting values, read with `{var:}`. They also reach scripts as environment variables unless something overrides them. Not preprocessed. |
| `variablesconfig` | OBJECT | Per-variable sources and options (§4). Not preprocessed. |
| `templates` | OBJECT | Named components for the `template` component; searched before template files. |
| `colours` | OBJECT | Named colours, e.g. `"accent": "#3478f6"`. |
| `pulse` | OBJECT | A repeating script (§8). |
| `iconpath` | STRING | Dock icon when the UI runs in its own window. |
| `log`, `debug` | OBJECT | §9. |

### `window`

Most keys matter only when the UI runs in its own window (launch mode 1).

| Key | Type | Default | Notes |
|---|---|---|---|
| `root` | OBJECT | | **Required.** The view tree. |
| `id` | STRING | | Lets actions target the window, e.g. `{"type": "function", "src": "<window id>", "args": "close"}`. |
| `title` | STRING | | Recommended. |
| `size` | OBJECT | 800 × 600 | `width`, `height`, 50–10000. Inside Alfred both are optional: width follows the theme, height shrinks to fit. |
| `minsize`, `maxsize` | OBJECT | | `width`, `height`. |
| `padding` | INTEGER | `0` | 0–32. |
| `blur` | BOOL | `true` | |
| `appearance` | ENUM | `"automatic"` | `automatic`, `light`, `dark`. |
| `movablebybackground` | BOOL | false outside Alfred, true inside | |
| `level` | INTEGER | `0` | An AppKit window level. Change it only with good reason. |
| `borderless` | BOOL | `false` | Drops the title bar options and enables `cornerradius`. |
| `cornerradius` | INTEGER | `0` | 0–128, borderless windows only. |
| `closeable`, `minimisable`, `resizeable`, `fullscreenable` | BOOL | `true` | |
| `fullsizecontentview` | BOOL | `false` | |
| `titlevisibility` | BOOL | `true` | |
| `titlebarappearstransparent` | BOOL | `false` | |
| `toolbar` | OBJECT | | Having one adds a toolbar. `type`: `unified` (default) or `unifiedcompact`. |
| `frameautosave` | BOOL | `false` | Remembers position and size per bundle location. Own window only. |

Window functions: `close`, `zoom`, `minimise`. To end a UI that runs inside Alfred, prefer the `finish` command over `close`.

Smallest useful `ui.json`:

```json
{
  "window": {
    "padding": 20,
    "root": { "type": "label", "text": "Nothing to show yet", "textalign": "centre", "font": { "size": "medium" } }
  }
}
```

A fuller top level, for a UI that opens in its own window and remembers a setting:

```json
{
  "bundleid": "com.example.notes",
  "iconpath": "../icon.png",
  "colours": { "muted": "#8e8e93" },
  "variablesconfig": {
    "query":      { "src": "args[0]" },
    "notes_dir":  { "src": "variable", "scriptenv": true },
    "show_dates": { "default": true, "persist": true, "scriptenv": true }
  },
  "window": {
    "id": "main", "title": "Notes", "frameautosave": true, "size": { "width": 900, "height": 600 },
    "toolbar": { "type": "unifiedcompact" },
    "root": {
      "type": "view", "layout": "border",
      "shortcuts": [ { "shortcut": "⎋", "action": { "type": "function", "src": "main", "args": "close" } } ],
      "events": "{file:components/root-events.json}",
      "components": [ "{file:components/search.json}", "{file:components/list.json}" ]
    }
  }
}
```

## 3. Placeholders

### Filled when the JSON is loaded

Alfred substitutes these in `ui.json` and in action JSON before parsing it.

| Placeholder | Becomes |
|---|---|
| `{var:name}` | the variable's value; the result is not scanned again |
| `{const:name}` | a workflow constant, e.g. `{const:alfred_workflow_cache}` (the same names as the `alfred_*` script environment) |
| `{file:path}` | the file's text, then processed further (so it may contain placeholders) |
| `{fileraw:path}` | the file's text with no further processing; faster for large row data |
| `{param:name}` | inside a template only: the usage's `params` value |

These keys are left alone at load time: `bundleid`, `variablesconfig`, `variables`, `args`, an action's `src`, `data.filter`.

### Filled when an action runs

`args`, `variables` and an action's `src` are resolved as the action fires, and may also use:

| Placeholder | Becomes |
|---|---|
| `{value:id.prop}` | a live property of a component; `self` is the component that owns the event |
| `{data:key}` | a value from the row of the dataview cell whose event is running |

In practice `{value:}` resolves in action `args` (including `finish.args` inside a `json` action), in action `variables` and in `data.filter`, and nowhere else. To use it in, say, `open.src` or an `update` value, copy it into the action's `variables` and read it back with `{var:}`:

```json
{ "type": "json", "variables": { "target": "{value:notes.selected.path}" },
  "src": { "open": { "type": "file", "src": "{var:target}" } } }
```

### Types and mixing

- A placeholder that is the whole string keeps the value's own type. `"behaviour": "{var:stream}"` with `stream` = `{"mode": "append", "scroll": "end"}` sets an object; booleans, numbers and arrays work the same way.
- A placeholder inside longer text always yields a string; non-string values are written as JSON: `"Showing {var:count} of {var:total}"`.
- In action args, an unresolved placeholder becomes `""`; objects become JSON; arrays become JSON unless `flattenarrayargs` is set.
- Pulse `args` take plain strings or a whole `{var:}` only, never mixed text.

### Ways to reuse JSON

- `"{file:components/x.json}"` anywhere a value goes: a child in `components`, the whole `events` value, an action.
- The `template` component with `params` (`components.md`, Reuse).
- A variable holding JSON, used as a whole-string placeholder, including whole actions: `"action": "{var:open_selected}"`.

## 4. Variables

Variables hold any JSON type. Read them with `{var:name}`.

Set them:
- at start: top-level `variables`, and the `src` / `default` / `persist` rules in `variablesconfig`;
- when an action runs: the action's own `variables` key;
- from a JSON action, including script output: the `variables` command.

`variablesconfig.<name>`:

| Key | Type | Default | Notes |
|---|---|---|---|
| `src` | STRING | | `"args[N]"`: launch argument N. `"args"`: all launch arguments as an array. `"variable"`: the workflow variable with the same name. |
| `default` | any | `null` | Used whenever the value is `null`; also the baseline for `persist`. |
| `persist` | BOOL | `false` | Saved when it differs from `default` and restored next launch. **Needs top-level `bundleid`.** |
| `scriptenv` | BOOL | `false` | Exported to scripts run by actions and the pulse. |

```json
"variablesconfig": {
  "folder": { "src": "args[1]", "default": "Inbox", "scriptenv": true },
  "theme":  { "default": "compact", "persist": true }
}
```

**The UI starts blind to the workflow.** Workflow variables (User Configuration, Arg and Vars, script output) are not visible inside the UI until you list each one in `variablesconfig` under the same name with `"src": "variable"`.

An action with only `variables` and no `type` is valid. **From example:** saving state on close, with `persist: true` on `draft`:
`{"triggers": ["quit"], "action": {"variables": {"draft": "{value:editor.text}"}}}`.

## 5. Actions

Events, shortcuts, menu items and `opendialog` run actions. Wherever an action goes, an array of actions may go instead; it runs as one compound action (Build 3145).

| Key | Type | Notes |
|---|---|---|
| `type` | ENUM | `log`, `script`, `json`, `function`. May be left out when the action only sets `variables`. |
| `src` | STRING or OBJECT | `script`: the script path. `json`: an object of commands, or a path to a `.json` file holding one. `function`: the target component id. `log`: unused. |
| `args` | STRING or ARRAY | `script`: argv. `function`: function name(s). `log`: the message, logged at info level. `json`: unused. |
| `variables` | OBJECT | Resolved as the action fires, before anything else, and set as variables. |
| `async` | BOOL | `false`: the UI waits. `true`: runs in the background and applies the output when it arrives, by which time the UI may have changed. |
| `flattenarrayargs` | BOOL | `false`. Pass array values as separate args instead of JSON. |

```json
{ "type": "script", "src": "scripts/search", "async": true,
  "args": ["{value:query.text}", "{value:sort.selected.value}", "{var:notes_dir}"] }
```

### What a script must do

- `src` is resolved against the bundle folder; `args` become argv. Don't rely on the working directory: resolve helper paths from the script's own location (`workflow.md` §7).
- **Its stdout is parsed as one JSON action**, the same object a `json` action takes as `src`. One reply can both set variables and update components: `{"variables": {"count": 2}, "update": {"ids": {"status": {"text": "2 notes"}}}}`.
- Empty stdout does nothing (**Inferred**). Write diagnostics to stderr.
- Environment: the workflow constants (`alfred_workflow_cache` and the rest), every variable with `scriptenv: true`, and the top-level `variables` values. Booleans passed as args arrive as `"1"` / `"0"` (**Inferred** from Try Alfred UI).
- An event's actions hold up the UI thread until they return. Return quickly or set `"async": true`.

```sh
#!/bin/zsh
# scripts/search: print one JSON action that fills the list
here=${0:A:h}
rows=$("$here/find-notes" "$1")   # your own code, printing a JSON array of rows
printf '{"update":{"ids":{"notes":{"data":{"src":%s}}}}}' "$rows"
```

## 6. JSON commands

A JSON action is an object of commands: the `src` of a `json` action, a `.json` action file, or a script's stdout.

- `variables` is applied first, so commands can read the new values with `{var:}`.
- `pulse` reconfigures the pulse, e.g. `{"pulse": {"interval": 0}}` stops it.
- The other commands always run in this fixed order, whatever order you write them in: `remove`, `insert`, `update`, `replace`, `sheet`, `share`, `sound`, `speak`, `copy`, `open`, `opendialog`, `window`, `notification`, `functions`, `popupmenu`, `finish`.

**Changing the component tree**

| Command | Keys | Example |
|---|---|---|
| `update` | `ids`: id → only the properties to change. `relayout` BOOL, default false: set it when the change alters sizes. | `{"update": {"ids": {"status": {"text": "Saved", "colour": "systemGreenColor"}}}}` |
| `insert` | `ids`: parent view id → ARRAY of components, added at the end. Relayouts. | `{"insert": {"ids": {"tags": [{"type": "label", "text": "new"}]}}}` |
| `replace` | `ids`: id → a whole new component. `retainids` BOOL, default true. Relayouts. | `{"replace": {"ids": {"body": {"type": "markdownarea", "text": "# Done"}}}}` |
| `remove` | `ids`: STRING or ARRAY. Relayouts. | `{"remove": {"ids": ["banner"]}}` |
| `sheet` | `root`: a view shown as a sheet. `id`: names it. `close`: the id of a sheet to close. `closeonescape` BOOL, default true; when false you must give `id` so code can close it. | `{"sheet": {"id": "settings", "root": {"type": "view", "padding": 16, "components": ["{file:components/settings.json}"]}}}` · `{"sheet": {"close": "settings"}}` |
| `window` | `resize`: `width`, `height` as INTEGER or `"auto"`; a missing or null key keeps the current value. | `{"window": {"resize": {"height": "auto"}}}` |
| `functions` | `ids`: id → function name or ARRAY of names. | `{"functions": {"ids": {"notes": "selectfirst"}}}` |
| `popupmenu` | `src`: the component to anchor to; `menu`: MENU items. | `{"popupmenu": {"src": "more", "menu": [{"text": "Rename", "action": {…}}]}}` |

**Side effects**

| Command | Keys | Example |
|---|---|---|
| `copy` | `type`: `text` (default), `file`, `url`. `src`: STRING or ARRAY, required. | `{"copy": {"type": "file", "src": ["~/Notes/a.md", "~/Notes/b.md"]}}` |
| `open` | `type`: `file` or `url`, required. `src`: STRING or ARRAY. | `{"open": {"type": "url", "src": "https://example.com/help"}}` |
| `share` | `type`: `file` or `url`, required. `src`: STRING or ARRAY. Opens the macOS share menu. | `{"share": {"type": "file", "src": "~/Notes/a.md"}}` |
| `sound` | `src`: a bundle-relative or absolute sound file, or the name of a file in `/System/Library/Sounds` without its extension. | `{"sound": {"src": "Tink"}}` |
| `speak` | `text`, required. | `{"speak": {"text": "Upload complete"}}` |
| `notification` | `post`: OBJECT or ARRAY of `{uid, title, text}`; `uid` defaults to a random UUID and reusing one replaces that notification. `remove`: uid or ARRAY of uids. A UI in its own window only shows a notification when the window isn't frontmost. | `{"notification": {"post": {"uid": "sync", "title": "Notes", "text": "Synced 12 notes"}}}` |
| `opendialog` | An open panel. `canchoosefiles` (default true), `canchoosefolders` (default false), `multiselect` (default false), `filetypes` (UTIs such as `public.image`), `folder`, `prompt`, `message`, `setvariable` (the variable that receives the path, or an array of paths with `multiselect`), `action` (run when the user confirms). | `{"opendialog": {"canchoosefolders": true, "canchoosefiles": false, "prompt": "Use folder", "setvariable": "dir", "action": {"type": "script", "src": "scripts/scan", "args": "{var:dir}"}}}` |

**Leaving the UI**

| Command | Keys | Example |
|---|---|---|
| `finish` | `args` (STRING or ARRAY), `variables` (OBJECT), `flattenarrayargs` (BOOL, default false). Closes the UI. In a workflow, `args` goes out of the object's output connection and `variables` join the workflow's variables. `{}` closes without passing anything. | `{"finish": {"args": "{value:notes.selected.path}", "variables": {"route": "open"}}}` |

## 7. Getting data in and out

**In**

| Source | How |
|---|---|
| The object's input (what was typed, a file from a Universal Action) | `variablesconfig: {"x": {"src": "args[0]"}}`, or `"src": "args"` for all of them |
| Workflow variables and User Configuration | `variablesconfig: {"x": {"src": "variable", "scriptenv": true}}`, same name |
| Workflow constants | `{const:alfred_workflow_data}` and friends in the JSON |
| Files at load | `{file:}`, `{fileraw:}` |
| Files at run time | `markdownarea.src`, `webkitview.src`, `imageview.image.src` |
| Live data | a script on the root `preload` or `launched` event, a button, or the pulse, printing `update`, `insert`, a dataview `data` change or `variables` |

**Out**

- `finish` is the only way to continue the workflow (`workflow.md` §4).
- Work done inside the UI needs no output: `copy`, `open`, `share`, `notification`, `sound`, `speak`, or a script.
- `log` actions and `log.internal: true` write to the workflow debugger when the UI runs inside Alfred.

## 8. Pulse

A script run on a timer; its stdout is applied as a JSON action. Configure it at the top level and change it later with the `pulse` command.

| Key | Type | Default | Notes |
|---|---|---|---|
| `src` | STRING | | Required. Script path, bundle-relative allowed. |
| `args` | STRING or ARRAY | | Plain strings or whole `{var:}` placeholders, re-read on every tick. No `{value:}`, no mixed text. |
| `interval` | DOUBLE | `0` | Seconds, 0.1–1000. `0` turns the pulse off. |
| `intervalmode` | ENUM | | `delay`: wait `interval` after each run ends. `regular`: tick at a fixed rate. |
| `now` | BOOL | `false` | Also run once right away, when the current event finishes. |

```json
"pulse": { "src": "scripts/poll", "interval": 2, "intervalmode": "delay", "now": true, "args": ["{var:job_id}"] }
```

A pulse that should stop when the job is done prints `{"pulse": {"interval": 0}, "update": {…}}`.

## 9. Logging and debugging

`log`:

| Key | Default | Notes |
|---|---|---|
| `level` | `none` | `none`, `error`, `warning`, `info`, `debug`, `verbose`, `all` |
| `internal` | `false` | Write to the workflow debugger (inside Alfred only). |
| `path` | | A log file; a relative path lands in Alfred UI's shared logs folder. |
| `console` | `false` | Also log to the system console. |
| `timestamp` | `false` | |
| `colourful` | `false` | ANSI colours, in files only. |

```json
"log": { "level": "all", "internal": true, "path": "~/Library/Logs/notes-ui.log", "timestamp": true }
```

`debug` (own window only): `reloadshortcut` (e.g. `"⌘r"`) reloads `ui.json` live; `colourful: true` paints each layout box a random colour.

The Try Alfred UI workflow (keyword `tryaui`) renders pasted snippets live.

## 10. Ranges at a glance

| What | Range |
|---|---|
| window `size` | 50–10000 (800 × 600 default in its own window) |
| window `padding` / `cornerradius` | 0–32 / 0–128 |
| view `padding`, `spacing` | 0–64 |
| view `cornerradius`, `border.width` | 0–32 |
| grid / flex `rows`, `cols` | 1–128 |
| flex `col`, `row` / spans / weights | 0–1024 / 1–1024 / 0.0–1.0 |
| constraint `insets` | 0–128 |
| dataview `cols` / `cell.height` | 1–16 / 12–1024 (default 64) |
| progress `thickness` | 0–32 |
| pulse `interval` | 0.1–1000 s |

Out-of-range numbers are clamped, not rejected.

## 11. Easy to get wrong

The core contracts are in `../SKILL.md`. Also:

- `persist` silently does nothing without `bundleid`.
- `shortcut` (STRING, any actionable component) and `shortcuts` (ARRAY, on a view) are different keys.
- Inside Alfred vs in its own window: stacking and `movablebybackground` differ; `reloadshortcut`, `frameautosave` and `toolbar` only work in a window.
- Button `bordershape` and `effect: "glass"` need macOS 26 or later.
- An action may be a `"{var:name}"` or `"{file:actions/x.json}"` placeholder, so several shortcuts and buttons can share one (**From example**).
- Some doc examples misspell keys; `components.md` lists them at the end.

## 12. Version history

- Alfred 6.0 (Build 3219, 18 Nov 2026) introduced Alfred UI and the Alfred UI workflow object. 6.0.1 (3221) and 6.0.2 (3222) list no Alfred UI changes.
- The workflow object is `alfred.workflow.userinterface.alfredui`, object version 1.
- Alfred 6 needs macOS 12 or later.
- Beta builds that changed the schema (useful when an older example disagrees):

| Build | Change |
|---|---|
| 3217 | progress default style renamed to `linear` |
| 3204 | `{fileraw:}` added; `predicate` filter removed |
| 3200 | `filter` moved into `data` with the `basic` filter; `file` component removed |
| 3196 | `elasticity` removed; dataview keys reorganised |
| 3189 | `automaticallyadjustscontentinsets` → `autoadjustcontentinsets`; picker `bordered` defaults to true |
| 3186 | `{param:}` allowed inside longer strings |
| 3184 | integer `size` constraint; absolute `{file:}` paths |
| 3180 | button `effect` (glass) and `bordershape` |
| 3157 | `placeholdercolour`; light/dark COLOUR object |
| 3156 | mixed-text placeholders; textfield/passwordfield `bordertype` → `bordered` |
| 3151 | `behaviour.selection` grouping; `hover` |
| 3145 | `events` and `action` take one item or an array; `urischemes` |
| 3129 | markdownarea `text` readable |
| 3127 | menu items without an action shown disabled |
