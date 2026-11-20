# Alfred UI components, layouts and value types

Look keys up here before writing a component. Facts come from the Alfred UI docs (https://www.alfredapp.com/help/alfredui/), the changelog and running Alfred 6.0; the wording and examples are this skill's own. Two labels mark facts the docs don't state: **Observed** (seen in a running Alfred 6.0) and **Inferred** (reasoned from examples).

Contents:
- [Notation](#notation)
- [Keys on every component](#keys-on-every-component)
- [Constraints](#constraints)
- [Events](#events)
- [Functions](#functions)
- [Containers: `view`](#view)
- [Text: `label`, `textfield`, `passwordfield`, `textarea`, `markdownarea`](#text-components)
- [Controls: `button`, `checkbox`, `picker`](#controls)
- [Display: `progress`, `imageview`, `webkitview`](#display-components)
- [`dataview`](#dataview)
- [Reuse: `template`, and the removed `file` component](#reuse)
- [Layouts](#layouts)
- [Value types: COLOUR, FONT, IMAGE, SHORTCUT, MENU](#value-types)
- [Readable properties](#readable-properties)
- [Where doc examples disagree with the reference](#where-doc-examples-disagree-with-the-reference)

## Notation

- Types: `STRING`, `BOOL`, `INTEGER`, `DOUBLE`, `ARRAY`, `OBJECT`, `ENUM` (one of the listed strings), and the value types at the end of this file (COLOUR, FONT, IMAGE, SHORTCUT, MENU).
- A number outside its range is clamped to the nearest end, not rejected.
- Setting a property to `null` puts it back to its default (for colours and images: removes it).
- **R** in a table means the property is readable with `{value:<id>.<prop>}` (or `{value:self.<prop>}` from the component's own event). See [Readable properties](#readable-properties).
- The 14 component types are: `view`, `label`, `button`, `checkbox`, `picker`, `textfield`, `passwordfield`, `textarea`, `markdownarea`, `progress`, `imageview`, `dataview`, `webkitview`, and the pseudo-type `template`. They wrap the matching AppKit controls.

## Keys on every component

| Key | Type | Default | Notes |
|---|---|---|---|
| `type` | ENUM | `"view"` | Leave it out and you get a view. |
| `id` | STRING | | Needed to read, update, replace, remove or call functions on the component. Must be unique across the whole UI, cells and templates included. |
| `constraints` | OBJECT | | Tells the parent's layout where and how big this component is. See [Constraints](#constraints). |
| `events` | ARRAY or one event | | See [Events](#events). A single event object is accepted since Build 3145. |
| `focus` | BOOL | | Put it on one component to give it keyboard focus when the UI opens. |
| `hidden` | BOOL | `false` | The component disappears but keeps its space in the layout. |
| `opacity` | DOUBLE | `1.0` | 0.0 to 1.0. |
| `enabled` | BOOL | `true` | `false` greys it out and ignores input. |
| `tooltip` | STRING | | Hover text. |
| `menu` | ARRAY of MENU | | Right-click menu. For a menu opened from code, use the `popupmenu` JSON command. |
| `shortcut` | STRING | | A key equivalent that fires the component's `actioned` event, e.g. `"⌘S"`. Works on actionable controls (buttons, checkboxes, pickers). Modifier glyphs: `⌘ ⇧ ⌃ ⌥ ↩︎`. Not the same as a view's `shortcuts` array. |
| `accessibility` | OBJECT | | `label`: a short name for VoiceOver (one capitalised word, no full stop, is Apple's advice). `help`: a sentence ending in a full stop, only when the effect of using the control isn't obvious. |

## Constraints

Set on a child; read by its parent's layout.

| Key | Type | Default | Values / notes |
|---|---|---|---|
| `region` | ENUM | | **Required in a `border` layout.** `top` and `bottom` span the full width; `left` and `right` take the height left over; `centre` takes whatever remains. |
| `position` | ENUM | `"fit"` | `fit`, `centre`, `top`, `right`, `bottom`, `left`, `topright`, `bottomright`, `bottomleft`, `topleft`. Anything but `fit` places the component at its own size inside its slot. |
| `stretch` | ENUM | `"none"` | `none`, `horizontal`, `vertical`. Only matters when `position` isn't `fit`. |
| `grid` | OBJECT | | **Required in a `flex` layout.** `col`, `row` (INTEGER 0–1024, default 0); `colspan`, `rowspan` (INTEGER 1–1024, default 1); `colweight`, `rowweight` (DOUBLE 0.0–1.0, default 0.0). |
| `insets` | OBJECT | | `top`, `right`, `bottom`, `left`: INTEGER 0–128, default 0. Added on top of the component's computed size. |
| `size` | OBJECT or INTEGER | | `width`, `height`: INTEGER, 0 means automatic. One integer sets both (Build 3184). In most layouts it behaves like a minimum. |

## Events

An event ties one or more triggers to an action.

```json
{ "id": "save", "type": "button", "text": "Save note",
  "events": [ { "triggers": ["actioned"], "action": { "type": "script", "src": "scripts/save", "async": true } } ] }
```

| Key | Type | Notes |
|---|---|---|
| `triggers` | ENUM or ARRAY | Default `"actioned"`. A component ignores triggers that don't apply to its type. |
| `action` | action or ARRAY | Required. An array runs as one compound action. The UI freezes until the actions return, so anything slow needs `"async": true`. Action keys are in `ui-json.md` §5. |
| `confirm` | OBJECT | Ask before running: `message`, `informativetext`, `iconpath`, `confirmbuttontext` (default "Confirm"), `cancelbuttontext` (default "Cancel"). |

Triggers:

| Trigger | Fires |
|---|---|
| `preload` | once the view tree is built, before the window appears (root view) |
| `launched` | once the window is up (root view) |
| `quit` | just before the UI closes (root view) |
| `actioned` | the control's main action: a button press, Return in a text field, a shortcut |
| `changed` | the value or selection changed through user input |
| `typingstopped` | the user paused typing; use it for heavy work on text |
| `mousedown`, `mouseup` | left mouse button down / up |
| `clicked`, `doubleclicked` | single / double click |

## Functions

Call them with an action `{"type": "function", "src": "<id>", "args": "<name>"}` (`args` may be an array), or with the JSON command `{"functions": {"ids": {"<id>": "<name>" | ["<name>", …]}}}`.

| Target | Functions |
|---|---|
| `picker` | `selectfirst`, `selectlast`, `selectprevious`, `selectnext` |
| `textarea` | `scrolltop`, `scrollbottom`, `caretstart`, `caretend` |
| `dataview` | `filterdata`, `scrolltop`, `scrollbottom`, `selectfirst`, `selectlast`, `selectprevious`, `selectnext`, `selectup`, `selectdown`, `selectleft`, `selectright`, `selectnone` |
| `webkitview` | `back`, `forward`, `reload` |
| the window (by `window.id`) | `close`, `zoom`, `minimise` |

## `view`

The only container. Its `layout` arranges its `components`. `{ "background": "systemGrayColor" }` alone is a valid view: type defaults to `view`, layout to `stack`.

| Key | Type | Default | Notes |
|---|---|---|---|
| `layout` | ENUM | `"stack"` | `stack`, `border`, `grid`, `inline`, `form`, `flex`. See [Layouts](#layouts). |
| `components` | ARRAY | | The children. May also be a `{var:}` or `{file:}` placeholder. |
| `padding` | INTEGER | `0` | 0–64. |
| `spacing` | INTEGER | `0` | 0–64, between children. |
| `direction` | ENUM | `"horizontal"` | `inline` layout only: `horizontal`, `vertical`. |
| `rows`, `cols` | INTEGER | `2` | `grid` and `flex` layouts: 1–128. |
| `cliptobounds` | BOOL | `false` | Clips children to the view. Costs a little on many complex views. |
| `cornerradius` | INTEGER | `0` | 0–32. |
| `appearance` | ENUM | `"inherit"` | `inherit`, `light`, `dark`. |
| `background` | COLOUR | | `null` clears it. |
| `border` | OBJECT | | `width` INTEGER 0–32 (default 0), `colour` COLOUR. Drawn inside the view's edge. |
| `focusable` | BOOL | `false` | Lets the view itself take focus. |
| `shortcuts` | ARRAY of SHORTCUT | | Active while focus is inside this view. When several views define the same key, the deepest one wins. |
| `vetomovablebybackground` | BOOL | `false` | Stops window dragging from this view's background. |

## Text components

### `label`

Short read-only text: titles, status lines, captions.

| Key | Type | Default | Notes |
|---|---|---|---|
| `text` | STRING **R** | | |
| `colour` | COLOUR | system text colour | |
| `font` | FONT | system font | |
| `selectable` | BOOL | `false` | Lets the user select and copy the text. |
| `linebreak` | ENUM | `"truncatetail"` | `truncatehead`, `truncatemiddle`, `truncatetail`, `wordwrap`, `charwrap`, `clip`. |
| `textalign` | ENUM | `"natural"` | `left`, `right`, `centre`, `justify`, `natural`. |

```json
{ "id": "status", "type": "label", "text": "3 notes", "colour": "secondaryLabelColor", "font": { "size": "small" } }
```

### `textfield`

Editable text, usually one line: the search field of a list UI.

| Key | Type | Default | Notes |
|---|---|---|---|
| `text` | STRING **R** | | |
| `placeholder` | STRING | | Grey hint while empty. |
| `placeholdercolour` | COLOUR | | Build 3157. |
| `multiline` | BOOL | `false` | When true, ⌥↩︎ or ⇧↩︎ adds a line. |
| `linebreak` | ENUM | `"scroll"` | `scroll`, `wrap`. (Not the label values.) |
| `font` | FONT | | |
| `colour` | COLOUR | | Text colour. |
| `background` | COLOUR | | `null` clears it. |
| `bordered` | BOOL | `true` | Use this, not `bordertype` (replaced in Build 3156). |
| `focusring` | BOOL | `true` | |
| `textinsets` | OBJECT | | `horizontal` (default 2), `vertical` (default 4), each 0–64. Vertical changes the field's height. |
| `editable`, `selectable` | BOOL | | |

Triggers: `changed` (each edit), `typingstopped`, `actioned` (Return).

```json
{ "id": "query", "type": "textfield", "placeholder": "Search notes", "focus": true, "focusring": false,
  "bordered": false, "font": { "size": "large" }, "constraints": { "region": "top" },
  "events": [
    { "triggers": ["changed"], "action": { "type": "function", "src": "notes", "args": "filterdata" } },
    { "triggers": ["actioned"], "action": { "type": "json", "src": { "finish": { "args": "{value:notes.selected.path}" } } } } ] }
```

### `passwordfield`

A text field that masks its input. Don't prefill `text` with a secret.

| Key | Type | Default |
|---|---|---|
| `text` | STRING **R** | |
| `font` | FONT | |
| `colour` | COLOUR | `textColor` |
| `background` | COLOUR | |
| `bordered` | BOOL | `true` |
| `focusring` | BOOL | `true` |
| `textinsets` | OBJECT | `horizontal` 2, `vertical` 4 (0–64) |

### `textarea`

Multi-line text, editable or read-only. Give it a `constraints.size`; it acts as a minimum.

| Key | Type | Default | Notes |
|---|---|---|---|
| `text` | STRING **R** | | |
| `font`, `colour`, `background` | | | |
| `bordertype` | ENUM | `"none"` | `bezel`, `solid`, `none`. (Textarea keeps `bordertype`; text fields use `bordered`.) |
| `editable`, `selectable` | BOOL | | |
| `behaviour` | OBJECT | | How a new `text` from code is applied. `mode`: `replace` (default), `append`, `prepend`, `replacelast`. `scroll`: `none` (default), `auto`, `start`, `end`. |
| `autoadjustcontentinsets` | BOOL | `true` | |
| `textinsets` | OBJECT | | `horizontal`, `vertical`: default 0, 0–64. |
| `disableallsubstitutions` | BOOL | `false` | `true` turns off smart quotes, smart dashes and spell checking. Use it for code or JSON. |

Triggers: `changed`, `typingstopped` (better for anything slow).

### `markdownarea`

Renders Markdown; links are clickable.

| Key | Type | Default | Notes |
|---|---|---|---|
| `text` | STRING **R** | | Markdown source, applied per `behaviour.mode`. Reading it returns the raw Markdown (Build 3129). |
| `src` | STRING | | A file to load instead, also applied per `behaviour.mode`. |
| `behaviour` | OBJECT | | Same `mode` and `scroll` as `textarea`. `append` + `scroll: "end"` suits streamed chat output. |
| `font`, `colour`, `background` | | | |
| `linespacing`, `lineheightmultiple`, `paragraphspacing`, `listspacing` | DOUBLE | | Typography. |
| `autoadjustcontentinsets` | BOOL | `true` | |
| `urischemes` | ARRAY | `["http", "https"]` | Link schemes that are clickable. Setting it replaces the list, so include `http` and `https` yourself. Applies to Markdown parsed after the change. |

## Controls

### `button`

| Key | Type | Default | Notes |
|---|---|---|---|
| `text` | STRING **R** | `"Button"` | |
| `image` | IMAGE **R** | | Icon or SF Symbol; `null` removes it. |
| `font` | FONT | | |
| `bordered` | BOOL | `true` | |
| `bordershape` | ENUM | `"auto"` | macOS 26+: `auto`, `capsule`, `roundedrectangle`, `circle`. |
| `effect` | ENUM | `"default"` | macOS 26+: `default`, `glass`. Apple's guidelines ask for glass sparingly. |
| `contenttintcolour` | COLOUR | | Tints the content of a borderless button. |

Triggers: `actioned` (normal click, with highlight and drag-off-to-cancel); `mousedown` replaces `actioned` and fires immediately, losing both. Add `"shortcut": "⌘↩"` to make a key press it.

```json
{ "type": "button", "text": "Copy link", "shortcut": "⌘C",
  "image": { "type": "symbol", "src": "link" },
  "events": [ { "triggers": ["actioned"], "action": { "type": "json", "variables": { "u": "{value:notes.selected.url}" },
    "src": { "copy": { "type": "url", "src": "{var:u}" } } } } ] }
```

### `checkbox`

| Key | Type | Default | Notes |
|---|---|---|---|
| `text` | STRING **R** | | Label to the right of the box; recommended. |
| `checked` | BOOL **R** | `false` | |

Trigger: `changed`. Read the state with `{value:self.checked}`.

### `picker`

A popup button with a list of choices.

| Key | Type | Default | Notes |
|---|---|---|---|
| `items` | ARRAY | | Each item: `text` STRING **R** (omit for a blank entry), `value` STRING **R** (unique), `type` ENUM `item` (default) or `separator` (ignores text and value). |
| `selected` | STRING **R** | | Write a `value` to select it. Reading gives an object, so read `selected.value` or `selected.text`. |
| `font` | FONT | | |
| `bordered` | BOOL | `true` | Build 3189. |
| `bordershape` | ENUM | `"auto"` | macOS 26+: `auto`, `capsule`, `roundedrectangle`. |

Trigger: `changed`. Functions: `selectfirst`, `selectlast`, `selectprevious`, `selectnext`.

```json
{ "id": "sort", "type": "picker", "selected": "recent",
  "items": [ { "text": "Most recent", "value": "recent" }, { "text": "Title", "value": "title" },
             { "type": "separator" }, { "text": "Size", "value": "size" } ],
  "events": [ { "triggers": ["changed"], "action": { "type": "script", "src": "scripts/load",
    "args": ["{value:sort.selected.value}"], "async": true } } ] }
```

## Display components

### `progress`

| Key | Type | Default | Notes |
|---|---|---|---|
| `progress` | DOUBLE **R** | `0.0` | 0.0–1.0. Change it with `{"update": {"ids": {"<id>": {"progress": 0.4}}}}`. |
| `style` | ENUM | `"linear"` | `linear` (a bar), `round` (a ring). `linear` replaced the old default name in Build 3217. |
| `thickness` | INTEGER | `0` | 0–32; 0 uses the style's own thickness. |
| `colour` | COLOUR | accent colour | Filled part. |
| `background` | COLOUR | | Track. |

### `imageview`

| Key | Type | Default | Notes |
|---|---|---|---|
| `image` | IMAGE **R** | | `null` removes it. |
| `resize` | ENUM | `"fit"` | `fit`, `fill`, `stretch`, `centre`. |
| `contenttintcolour` | COLOUR | | Tints SF Symbols. **Observed:** `file` images are never tinted. |
| `background` | COLOUR | | |
| `cornerradius` | INTEGER | `0` | 0–32, rounds the view, not the picture inside it. |

```json
{ "id": "preview", "type": "imageview", "resize": "fill", "cornerradius": 8,
  "image": { "type": "file", "src": "resources/empty.png" } }
```

### `webkitview`

A web view. Give it a `constraints.size`.

| Key | Type | Default | Notes |
|---|---|---|---|
| `src` | STRING **R** | | URL or file path to load. |
| `text` | STRING | | HTML to render directly. |
| `openlinksexternally` | BOOL or regex STRING | `false` | `false` keeps every link inside the view; a regex sends matching links to the default browser. |

Trigger: `changed` (the URL changed). Functions: `back`, `forward`, `reload`.

**Observed** in Alfred 6.0:
- `changed` fires when navigation starts, before anything is drawn. No event reports that loading finished. Hash changes and iframe navigation don't fire it; only main-frame URLs reach the UI.
- The page lays out at the view's own CSS width, so a narrow pane shows a site's mobile layout.
- `back` and `forward` walk one history across every `src` you set, so back may land on the previous item's page. Drive an address field from `changed`, not from your own selection.
- `hidden: true` leaves the last page showing; fade with `opacity` instead.

Recipes for a placeholder until load and a desktop layout in a narrow pane: `examples.md`, Web page idioms.

## `dataview`

A list or grid built from one cell design plus one data object per row. Cells are reused as the user scrolls.

| Key | Type | Default | Notes |
|---|---|---|---|
| `cell` | OBJECT | | `root`: the view drawn per row (required). `height`: INTEGER 12–1024, default 64. `init`: values applied to a reused cell before its row data, to reset it. `selected`: values applied on top for the selected row. `init` and `selected` use the same `"<cellId>.<prop>"` keys as rows. |
| `data` | OBJECT | | Rows and filter, see below. Required, but can arrive later through `update`. |
| `cols` | INTEGER | `1` | 1–16. Above 1 the rows flow into a grid, left to right. (The Build 3148 changelog calls it `colcount`; the docs and examples use `cols`.) |
| `placeholder` | STRING | | Shown when there are no rows. |
| `padding`, `spacing` | INTEGER | `0` | 0–64. |
| `autoadjustcontentinsets` | BOOL | `true` | |
| `behaviour` | OBJECT | | `selection`: `wrap` (`none` default, `vertical`), `allowempty` (BOOL, default false; with nothing selected `changed` passes `null`), `hover` (BOOL, default false; pointer movement selects and fires `changed`). |
| `select` | STRING | | A row `uid` to select; wins over the reselection done by `modify`. An empty or unknown uid clears the selection (see `allowempty`). |

Trigger: `changed` (selection). Functions: see [Functions](#functions); `selectnext` and `selectprevious` wrap across grid rows, the four directional ones move in the grid.

Rows:
- `"<cellId>.<prop>": value` sets a property on a component inside the cell (`"title.text"`, `"icon.image"`).
- A key without a dot (`"path"`) is a hidden value. Nothing shows it, but filters, `{data:path}` in cell events and `{value:<dataviewId>.selected.path}` can read it (**Observed**).
- `uid` is reserved: give every row a stable one so filtering and updates keep the selection.
- Read the selected row with `{value:<dataviewId>.selected.<cellId>.<prop>}` or `{value:<dataviewId>.selected.<key>}`.

### `data` with the `basic` provider

| Key | Type | Notes |
|---|---|---|
| `type` | ENUM | `basic` (the default and only provider). |
| `src` | ARRAY of OBJECT | Required. The rows. `"{fileraw:resources/rows.json}"` loads a big list quickly. |
| `filter` | OBJECT | See below. |
| `modify` | OBJECT | Edits the current rows instead of replacing them. `insert`: `src` ARRAY, `uid` (anchor row), `position` `after` (default) or `before`, `autoselect` BOOL (default true). `replace`: `srcmap` OBJECT (uid → new row), `autoselect`. `delete`: `uids` ARRAY, `autoselect`. |

To replace rows at run time, a script prints `{"update": {"ids": {"<dataviewId>": {"data": {"src": [ … ]}}}}}`; put `modify` inside `data` for partial edits (**Inferred** shape, confirmed by working examples).

### The `basic` filter

Word search like Alfred's own result matching. `data.filter` is not preprocessed, so a `{value:}` in `match` is read again every time the filter runs.

| Key | Type | Default | Notes |
|---|---|---|---|
| `type` | ENUM | `"basic"` | |
| `args` | STRING or ARRAY | | Required. Row key(s) to search, e.g. `"title.text"`. A hidden key such as `"keywords"` lets you search text the cell doesn't show. |
| `match` | STRING | | Required. The search text, e.g. `"{value:query.text}"`. |
| `matchmode` | ENUM | `"exactfromstartorwhitespace"` | `exactfromstartorwhitespace`, `exactfromstart`, `wordmatchanyorder`, `wordmatchsequential`. |
| `matchempty` | BOOL | `true` | An empty search shows every row. |

The filter never runs by itself: call `filterdata`, usually from the search field's `changed` event.

```json
{ "id": "notes", "type": "dataview", "cols": 1, "placeholder": "No notes",
  "constraints": { "region": "centre" },
  "cell": {
    "height": 44,
    "init": { "row.background": null, "title.colour": "labelColor" },
    "selected": { "row.background": "alfredSelectedResultBackgroundColor", "title.colour": "alfredSelectedResultTextColor" },
    "root": { "id": "row", "type": "view", "layout": "inline", "direction": "vertical", "padding": 6,
              "components": [ { "id": "title", "type": "label" },
                              { "id": "folder", "type": "label", "colour": "secondaryLabelColor", "font": { "size": "small" } } ] } },
  "data": {
    "filter": { "args": ["title.text", "folder.text"], "match": "{value:query.text}", "matchmode": "wordmatchanyorder" },
    "src": [ { "uid": "n1", "title.text": "Groceries", "folder.text": "Home", "path": "~/Notes/groceries.md" },
             { "uid": "n2", "title.text": "Sprint plan", "folder.text": "Work", "path": "~/Notes/sprint.md" } ] } }
```

## Reuse

### `template`

Stamps out a component defined once, filling `{param:<name>}` slots.

| Key | Type | Notes |
|---|---|---|
| `src` | STRING | A name from the top-level `templates` object, or a bundle-relative `.json` file. Names are looked up first. |
| `params` | OBJECT | Values for `{param:}` slots, substituted when the template is used. Since Build 3186 a slot can sit inside a longer string. |

`id` and `constraints` on the template usage replace any inside the template. Keep ids out of templates, or build them from a param, since ids must stay unique.

```json
"templates": { "tag": { "type": "button", "bordershape": "capsule", "text": "{param:name}" } },
…
{ "type": "template", "src": "tag", "id": "tag-home", "params": { "name": "Home" } }
```

### `file` component: removed

`"type": "file"` on a component was removed in Build 3200, although some doc pages still describe it. Inline a fragment with a `"{file:components/x.json}"` placeholder, or use a template with a file `src`. The IMAGE type `"file"` is a different thing and still valid.

## Layouts

Set `layout` on a `view`. Each layout reads different constraints from the children.

| Layout | View keys | How children are placed |
|---|---|---|
| `stack` | `padding` | All children fill the view on top of each other; the first is at the back. The view wants the size of its largest child. |
| `border` | `padding`, `spacing` | Each child names a `region`. `top`/`bottom` get their own height across the full width; `left`/`right` get their own width over the height that's left; `centre` gets the rest. |
| `grid` | `rows`, `cols` (1–128, default 2), `padding`, `spacing` | Equal cells, filled left to right, top to bottom. `{}` leaves a cell empty. |
| `inline` | `direction` (`horizontal` default, `vertical`), `padding`, `spacing` | One after another at their own size. `position` and `stretch` adjust each one. |
| `form` | `padding`, `spacing` | Children pair up as label, field, label, field… The label column is as wide as its widest label. `{}` fills an empty slot. |
| `flex` | `rows`, `cols` (1–128, default 2), `padding`, `spacing` | Each child gives `constraints.grid`: cell, spans and weights. Weights share out spare space. |

```json
{ "type": "view", "layout": "form", "padding": 12, "spacing": 8, "components": [
  { "type": "label", "text": "Title" }, { "id": "t", "type": "textfield" },
  { "type": "label", "text": "Folder" }, { "id": "f", "type": "picker", "items": [ { "text": "Home", "value": "home" } ] },
  {}, { "type": "button", "text": "Create", "shortcut": "↩" } ] }
```

```json
{ "type": "view", "layout": "flex", "cols": 2, "rows": 1, "spacing": 8, "components": [
  { "constraints": { "grid": { "col": 0, "row": 0, "colweight": 0.4, "rowweight": 1 } }, "id": "list", "type": "dataview", "cell": { "root": { "id": "c" } } },
  { "constraints": { "grid": { "col": 1, "row": 0, "colweight": 0.6, "rowweight": 1 } }, "id": "detail", "type": "markdownarea" } ] }
```

**Observed:** `inline` centres a child that is narrower than its line, so an icon + label row drifts to the middle. For a left-aligned icon and text, use `border`: the icon in `region: left`, the label in `region: centre` with `position: left, stretch: horizontal`.

## Value types

### COLOUR

Any of:
- hex: `"#3478f6"`, or with alpha `"#3478f680"`
- `"rgb(52, 120, 246)"`, `"rgb(52, 120, 246, 0.5)"`
- `"hsv(217, 79, 96)"`, `"hsv(217, 79, 96, 0.5)"`
- a name from the top-level `colours` object
- Alfred's theme colours `alfredSelectedResultTextColor`, `alfredSelectedResultBackgroundColor`
- an AppKit colour name, including the adaptive ones: `labelColor`, `secondaryLabelColor`, `systemBlueColor`, `controlBackgroundColor`
- an object `{"light": "<colour>", "dark": "<colour>"}` that follows the appearance (Build 3157; not on the property page)

Colour names keep Apple's US spelling; the property keys are British (`colour`).

### FONT

| Key | Values | Default |
|---|---|---|
| `size` | a number of points, or `default`, `hairline`, `extrasmall`, `small`, `medium`, `large`, `extralarge`, `ginormous` | `default` |
| `weight` | `ultralight`, `thin`, `light`, `regular`, `medium`, `semibold`, `bold`, `heavy`, `black` | `regular` |
| `width` | `compressed`, `condensed`, `standard`, `expanded` (proportional fonts only) | `standard` |
| `monospaced` | `true`, `false`, or `"digits"` (only figures fixed-width, good for counters) | `false` |

### IMAGE

| Key | Notes |
|---|---|
| `type` | `file` (default): an image file. `fileicon`: the Finder icon of the file or app at `src`. `filetypeicon`: the icon for a file type. `symbol`: an SF Symbol name. |
| `src` | Required. Path, app path, type or symbol name. No type takes a URL: download remote images to `alfred_workflow_cache` and pass the path. |
| `size` | `width`, `height` INTEGER, 0 = automatic. Give one and the other follows the aspect ratio. |

### SHORTCUT

An entry of a view's `shortcuts` array: `{ "shortcut": "⌘D", "action": { … } }`. `action` may be an array. Write keys as glyphs: `"⎋"`, `"↩"`, `"⌘↩"`, `"↑"`, `"↓"`, `"←"`, `"→"`.

### MENU

An entry of `menu` (on a component) or of `popupmenu.menu` (JSON command).

| Key | Values |
|---|---|
| `type` | `text` (default) or `separator`, lower case |
| `text` | STRING |
| `state` | `off` (default), `on` (tick), `mixed` (dash) |
| `action` | action or ARRAY. An item without one appears disabled (Build 3127). |
| `submenu` | ARRAY of menu items; the item's own `action` is then ignored |

## Readable properties

`{value:<id>.<prop>}` reads a live value; `self` stands for the component whose event is running. It resolves only in action `args`, action `variables` and `data.filter` (`ui-json.md` §3).

| Component | Readable |
|---|---|
| `label` | `text` |
| `button` | `text`, `image` |
| `checkbox` | `text`, `checked` |
| `picker` | `selected.value`, `selected.text` |
| `textfield`, `passwordfield`, `textarea` | `text` |
| `markdownarea` | `text` (raw Markdown) |
| `progress` | `progress` |
| `imageview` | `image` |
| `webkitview` | `src` |
| `dataview` | `selected.<cellId>.<prop>`, `selected.<hiddenKey>`, `selected.uid` |

## Where doc examples disagree with the reference

The reference tables are right; some examples on the doc pages are not. Don't copy these spellings from them:

| In a doc example | Use |
|---|---|
| `"trigger"`, `"trigers"` | `"triggers"` (the examples only work because `actioned` is the default) |
| `"color"` on a progress bar | `"colour"` |
| `"bordertype"` on a textfield | `"bordered": false` |
| `"type": "Separator"` in a menu | `"separator"` |
| `behaviour.allowemptyselection` in the dataview `select` note | `behaviour.selection.allowempty` |
| view `appearance: "dark"` described as forcing light | it forces dark |
| a trailing comma in the first textarea snippet | valid JSON |
