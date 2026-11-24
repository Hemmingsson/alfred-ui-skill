---
name: alfred-ui
description: 'Builds Alfred 6 "Alfred UI" windows (`.alfredui` bundles with `ui.json`: views, layouts, dataview lists, webkitview, actions, UI scripts) and wires them into Alfred workflows via the `alfred.workflow.userinterface.alfredui` object. Use when creating or editing an Alfred workflow that shows its own window, panel, list, form or dashboard, when touching `ui.json` or a `.alfredui` folder, or when the user mentions Alfred UI or Alfred 6, even if they only say "Alfred workflow with a UI". Not for classic Script Filter result lists.'
---

# Alfred UI

Alfred UI arrived in Alfred 6.0. It is separate from Alfred 5's Script Filters, Text View and Grid View, so take every key, value and placeholder from `references/` or a real example. When neither settles a question, tell the user what you guessed.

## Model

- A trigger's argument enters the **Alfred UI object** as `args[0]`. The object loads `<name>.alfredui/ui.json` (the `window.root` view tree), and its output fires only on a `finish` action (`args` + `variables`).
- Component **events** run **actions**: `json` (JSON action commands: update, open, copy, finish…), `script` (a bundle script whose stdout is one JSON action), or `function` (a component function: filterdata, selectnext…).
- `update` commands change the live view tree.

## Build steps

1. **Shape.** Decide launch mode: inside Alfred (`launchmode` 0) for a pick-and-go panel, or an external window (1) for a tool that stays open. Choose components for the requested interaction: for example, a `dataview` for a picker, fields and buttons for a form, or labels and `progress` for a status panel. Add a detail pane only when the task needs one. Done when the view tree supports the requested actions and each component is described in `references/components.md`.
2. **Find a precedent.** Open the example in `references/examples.md` closest to your pattern and read its `ui.json`. Use it to check API syntax and event wiring; adapt its layout, data model and behaviour to the task.
3. **Bundle.** Write `<name>.alfredui/ui.json` plus `scripts/` (shebang, `chmod +x`, no extension needed). Paths inside the UI are relative to the bundle root.
4. **Data in.** Map launch args and workflow variables in `variablesconfig`. Load runtime data from a script on the root view's `preload` or `launched` event (`"async": true`) that prints an `update` action. Done when every `{var:}` you read has a declared source.
5. **Data out.** Every route that should continue the workflow ends in `finish` with `args` and/or `variables`. Side effects that keep the UI open use JSON commands (`open`, `copy`, `notification`). Route several exits with `finish.variables` plus a Conditional downstream.
6. **Wire the workflow.** Add the object, connections and `uidata` to `info.plist` (`references/workflow.md`). `info.plist` must be an XML plist. Secrets and settings go in User Configuration, imported with `"src": "variable", "scriptenv": true`.
7. **Verify.** Run the checker that ships with this skill, `python3 <skill-dir>/scripts/check_ui.py <workflow-folder>`, where `<skill-dir>` is the folder holding this SKILL.md (use its absolute path; the checker works from any working directory). Repeat until it reports 0 errors. Run `plutil -lint info.plist`. Run each UI script by hand with sample env and args, and confirm its stdout parses as one JSON action. Done when all three pass. Report anything that only Alfred can show (layout, focus, rendering) as unverified.

## Contracts

These hold in every UI. Each line is a mistake agents make without it.

- **Script stdout is one JSON action** (`{"update":…}`, `{"variables":…,"update":…}`). Print nothing else to stdout; diagnostics go to stderr. Empty stdout does nothing.
- **Scripts receive argv from `args`** and env from variables marked `scriptenv: true` (plus `variables` initial values). Workflow variables are invisible to the UI unless declared `"src": "variable"`.
- **`{value:id.prop}`** resolves in any action `args` (including `finish.args` inside a `json` action), in action `variables` and in `data.filter`. Anywhere else, copy it into the action's `variables` and read `{var:}`.
- **Every `id` is globally unique**, including ids inside dataview cells and templates.
- **Dataview rows** are objects. A `"<cellId>.<prop>"` key fills a cell component (`"title.text"`, `"thumb.image"`). A plain key without a dot (`"url"`) is a hidden value: nothing shows it, but filters, `{data:url}` and `{value:<dataviewId>.selected.url}` read it. `uid` is reserved: set it to a stable id so selection survives updates. Read a cell with `{value:<dataviewId>.selected.<cellId>.<prop>}`.
- **Filtering runs only when called:** a textfield `changed` event runs the dataview's `filterdata` function.
- **In search + list UIs, keyboard focus stays on the text field.** Put Return, ⌘-shortcuts and arrow handling on the focused field's events or on the root view's `shortcuts`, calling dataview functions (`selectnext`, `selectprevious`).
- **Slow work blocks the UI** unless the action is `"async": true`. Show a placeholder or `progress` while it runs; heavy per-keystroke work uses `typingstopped`.
- **`update` does not re-layout** unless `"relayout": true`; set it when sizes change.
- **British spellings**: `colour`, `centre`, `behaviour`, `minimise`. Colour constant names keep Apple's US spelling (`systemOrangeColor`, `alfredSelectedResultTextColor`). The event key is `triggers`, not `trigger`. Doc examples contain typos; the reference tables in `references/` are right.

## References

Read only what the current step needs:

- `references/components.md`: before writing any component, layout, constraint, COLOUR/FONT/IMAGE value or event trigger. It has a table of contents.
- `references/ui-json.md`: top-level `ui.json` keys, placeholders (`{var:}`, `{file:}`, `{fileraw:}`, `{value:}`, `{data:}`), variables, actions, every JSON action command, pulse (polling), logging and debugging.
- `references/workflow.md`: the Alfred UI object in `info.plist`, inputs, `finish` outputs, Conditionals, packaging and installing.
- `references/examples.md`: real, working `ui.json` files on GitHub grouped by pattern (list/picker, list + detail, form, dashboard, chat, confirm/error, live tester), plus reusable interaction patterns and design considerations.

Test snippets live in Alfred with the official Try Alfred UI workflow (keyword `tryaui`). Doc root: https://www.alfredapp.com/help/alfredui/
