# Wiring an Alfred UI into a workflow

How the Alfred UI object sits in `info.plist`, how data enters and leaves it, routing, packaging and installing.

Contents:
- [1. A minimal complete info.plist](#1-a-minimal-complete-infoplist)
- [2. The Alfred UI object](#2-the-alfred-ui-object)
- [3. Inputs](#3-inputs)
- [4. Outputs](#4-outputs)
- [5. Routing several exits](#5-routing-several-exits)
- [6. Common neighbour objects](#6-common-neighbour-objects)
- [7. Scripts: working directory and environment](#7-scripts-working-directory-and-environment)
- [8. Package, install, debug](#8-package-install-debug)

Sources: https://www.alfredapp.com/help/workflows/user-interface/alfredui/ and the real `info.plist` files listed in `examples.md`. **FROM EXAMPLE** marks facts seen in code but not stated in the docs.

## 1. A minimal complete info.plist

Adapted from [aboustayyef/alfredq](https://github.com/aboustayyef/alfredq/blob/main/info.plist), shown as JSON for readability. **`info.plist` must be an XML property list.** Write it as JSON if that is easier, then run `plutil -convert xml1 info.plist` and `plutil -lint info.plist` before Alfred sees it. Don't leave it as JSON or binary.

```json
{
  "bundleid": "com.example.myworkflow",
  "name": "My Workflow",
  "description": "One line",
  "createdby": "Author",
  "version": "1.0.0",
  "disabled": false,
  "objects": [
    { "uid": "2C93813B-35B0-4A5F-83A7-A2298C61EDB5", "type": "alfred.workflow.input.keyword", "version": 1,
      "config": { "keyword": "{var:keyword}", "argumenttype": 1, "withspace": true,
                  "text": "My Workflow", "subtext": "Open the window" } },
    { "uid": "91E2A1C8-3B85-41E7-B706-BE3520A92269", "type": "alfred.workflow.userinterface.alfredui", "version": 1,
      "config": { "path": "answer.alfredui", "launchmode": 0, "stackview": false } }
  ],
  "connections": {
    "2C93813B-35B0-4A5F-83A7-A2298C61EDB5": [
      { "destinationuid": "91E2A1C8-3B85-41E7-B706-BE3520A92269", "modifiers": 0, "modifiersubtext": "", "vitoclose": false }
    ]
  },
  "uidata": {
    "2C93813B-35B0-4A5F-83A7-A2298C61EDB5": { "xpos": 80,  "ypos": 80 },
    "91E2A1C8-3B85-41E7-B706-BE3520A92269": { "xpos": 300, "ypos": 80 }
  },
  "userconfigurationconfig": [
    { "variable": "api_key", "type": "textfield", "label": "API Key",
      "description": "Read by the UI scripts as $api_key",
      "config": { "default": "", "placeholder": "", "required": true, "trim": true } },
    { "variable": "keyword", "type": "textfield", "label": "Keyword",
      "config": { "default": "myw", "placeholder": "", "required": false, "trim": true } }
  ]
}
```

- `uid`s are uppercase UUIDs (`uuidgen`). Every object needs a `uidata` position; space them about 220 px apart.
- Keywords need at least 3 characters: the Alfred Gallery rejects shorter ones, and short ones clash with other workflows.
- Keyword `argumenttype`: `0` required, `1` optional, `2` none.
- `userconfigurationconfig` values appear in the workflow's Configure sheet. The user's values become workflow variables. The UI sees them only through `variablesconfig` (§3), e.g. `"api_key": { "src": "variable", "scriptenv": true }`.

## 2. The Alfred UI object

```json
{ "type": "alfred.workflow.userinterface.alfredui", "version": 1,
  "config": { "path": "name.alfredui", "launchmode": 0, "stackview": false } }
```

| key | values | meaning |
|---|---|---|
| `path` | relative path | The bundle folder, relative to the workflow root. It can be in a subfolder: `"ui/confirm.alfredui"`. |
| `launchmode` | `0` / `1` | `0` opens inside the Alfred window, sized to the theme width (a pick-and-go panel). `1` opens its own movable, resizable window (a tool that stays open). |
| `stackview` | bool | `true` stacks the UI on the current Alfred view, so ⎋ returns to it (⌘⎋ hides Alfred). It applies to `launchmode` 0 only. |

- **Choosing the mode at run time (FROM EXAMPLE).** Put a JSON Utility before the UI that emits `{"alfredworkflow":{"arg":"{query}","config":{"launchmode":"{var:launch_external}"}}}`, so a user-config checkbox decides (mobile-web-tester).
- One workflow can hold several UI objects, and two objects can share one `path` with different modes.

## 3. Inputs

| Source | How the UI receives it |
|---|---|
| The object's input argument (`{query}`) | `variablesconfig: { "x": { "src": "args[0]" } }`. `"src": "args"` gives all args as an array. |
| Several values as args | Upstream, join them with tabs and add a Split Arg utility (Split with Tab, Output as Arguments). Then use `args[0]`, `args[1]`, … (hackerboard). |
| Workflow variables, User Configuration, Arg and Vars, script `alfredworkflow.variables` | `variablesconfig: { "x": { "src": "variable", "scriptenv": true } }`, with the same name. **Without this the UI cannot see them.** |
| Workflow constants | `{const:alfred_workflow_data}`, `{const:alfred_workflow_cache}` and the others, in `ui.json`. Scripts get the standard `alfred_*` env vars without declaring them (FROM EXAMPLE). |

Triggers that can launch a UI: Keyword, Hotkey, Universal Action, External Trigger, or any object's output (Run Script, Script Filter, Conditional, Arg and Vars, JSON Utility).

## 4. Outputs

- The UI object's output connection fires **only** when the UI runs a `finish` JSON action: `{"finish":{"args":"…","variables":{…}}}`.
  - `args` (string or array) becomes `{query}` and `$1` downstream.
  - `variables` merge into the workflow stream as `{var:name}`.
  - `{"finish":{}}` closes the UI without passing anything on.
- Closing with ⎋ or the window close button continues nothing.
- A UI that does its work itself (`open`, `copy`, scripts) needs nothing connected after it.

## 5. Routing several exits

One UI, several outcomes (open vs copy, confirm vs cancel): every exit runs `finish` with a distinguishing variable, and a Conditional after the UI routes on it.

```json
{ "type": "json", "src": { "finish": { "args": "{value:list.selected.url}", "variables": { "route": "open" } } } }
```

Conditional config (FROM EXAMPLE, Rex):

```json
{ "type": "alfred.workflow.utility.conditional", "version": 1, "config": {
  "conditions": [
    { "uid": "<UUID-A>", "inputstring": "{var:route}", "matchmode": 0, "matchstring": "open", "matchcasesensitive": false, "outputlabel": "Open" },
    { "uid": "<UUID-B>", "inputstring": "{var:route}", "matchmode": 0, "matchstring": "copy", "matchcasesensitive": false, "outputlabel": "Copy" } ],
  "elselabel": "else", "hideelse": true } }
```

Each branch is a connection out of the Conditional that carries `"sourceoutputuid": "<UUID-A>"` (the condition's uid). The else branch has no `sourceoutputuid`. `matchmode`: `0` is equal, `1` not equal, `4` regex (INFERRED from the UI order: is equal, is not equal, greater, less, matches regex).

Often a Conditional is unnecessary: side effects such as `open` and `copy` can run inside the UI (§4).

## 6. Common neighbour objects

| Object | type, version | config |
|---|---|---|
| Keyword | `alfred.workflow.input.keyword`, 1 | `keyword`, `argumenttype`, `withspace`, `text`, `subtext` |
| Hotkey | `alfred.workflow.trigger.hotkey`, 2 | `hotkey` 0 and `hotmod` 0 leave it unset for the user to assign |
| Open URL | `alfred.workflow.action.openurl`, 1 | `url: "{query}"`, `browser: ""` |
| Copy to Clipboard | `alfred.workflow.output.clipboard`, 3 | `clipboardtext: "{query}"`, `autopaste: false`, `transient: false` |
| Conditional | `alfred.workflow.utility.conditional`, 1 | §5 |
| Run Script | `alfred.workflow.action.script`, 2 | `type`, `script`, `scriptfile`, `scriptargtype` 1 (argv). See below. |

Run Script and Script Filter `type` (FROM EXAMPLE, checked against installed workflows):

| `type` | Runs | Fill |
|---|---|---|
| `8` | an external, executable file (any language, chosen by its shebang) | `scriptfile`: path relative to the workflow folder; `script` empty |
| `0` | inline `/bin/bash` | `script` |
| `5` | inline `/bin/zsh` | `script` |
| `11` | inline `/bin/zsh --no-rcs` | `script` |
| `7` | inline JavaScript for Automation | `script` |

`11` is inline zsh, not an external file: with `type` 11 Alfred runs the `script` text, not `scriptfile`. For a script kept in a file, use `8` and `chmod +x` the file.

Copy the full config from an example's `info.plist` when you use any other object.

## 7. Scripts: working directory and environment

- Script `src` paths and `{file:}` paths resolve against the bundle root. alfredapp's scripts assume the working directory *is* the bundle root (`./scripts/common`). Third-party scripts resolve paths from their own location (`$(dirname "$0")`, `__file__`). Do the latter: it is safe either way.
- `info.plist` scripts (Run Script, Script Filter) run from the workflow root and reach bundle scripts as `./name.alfredui/scripts/x`. One script can serve both a Script Filter and the UI when a mode argument chooses the output shape (mobile-web-tester).
- UI script environment: variables with `scriptenv: true` (arrays and objects arrive as JSON strings, booleans as `"1"` and `"0"`), plus the standard `alfred_workflow_*` vars, plus `alfred_ui_source` (the id of the component that fired the event). An unset value passed as an arg arrives as `"<null>"` (INFERRED from alfred-go's handling).
- Error handling: catch errors and return them as a UI update (a red label, a placeholder, `{"sound":{"src":"Basso"}}`), and exit 0. Alfred drops a failing script's stderr unless `log` is configured.

## 8. Package, install, debug

- **Package:** `cd <workflow-folder> && zip -r ../Name.alfredworkflow . -x '.*'`. `info.plist` must be at the zip root. Keep the executable bits.
- **Install:** `open Name.alfredworkflow` opens Alfred's import dialog. While developing, edit the installed copy directly: Alfred Preferences, right-click the workflow, Open in Finder.
- **Debug:** set `"log": {"level": "all", "internal": true}` in `ui.json`, then open the workflow debugger (the bug icon in Alfred Preferences). `{"type":"log","args":"…"}` actions write to the debugger. For an external window, `"debug": {"reloadshortcut": "⌘r", "colourful": true}` reloads `ui.json` live and colours the layout boxes.
- **Reload after replacing the installed folder:** Alfred keeps the old objects (new keywords missing) until `osascript -e 'tell application id "com.runningwithcrayons.Alfred" to reload workflow "<bundleid>"'`.
- **Seeing the window is the user's step.** Typing a keyword with `search "…"` and sending Return through System Events opens whatever result is on top, often a file from file search. The window also closes as soon as the user moves focus. To open it from a script, give the workflow an External Trigger (`alfred.workflow.trigger.external`, `triggerid`) wired to the UI and call `osascript -e 'tell application id "com.runningwithcrayons.Alfred" to run trigger "<id>" in workflow "<bundleid>"'`, then `screencapture -l <window id> shot.png`. Without one, ask the user to open the window. List Alfred's on-screen window ids and titles with:
  ```sh
  swift - <<'EOF'
  import CoreGraphics
  let windows = CGWindowListCopyWindowInfo(.optionOnScreenOnly, kCGNullWindowID) as? [[String: Any]] ?? []
  for w in windows where (w[kCGWindowOwnerName as String] as? String ?? "").hasPrefix("Alfred") {
      print(w[kCGWindowNumber as String] ?? "", w[kCGWindowOwnerName as String] ?? "", w[kCGWindowName as String] ?? "")
  }
  EOF
  ```
- **Iterate on layout** in the Try Alfred UI workflow (keyword `tryaui`): paste a component tree and see it render.
