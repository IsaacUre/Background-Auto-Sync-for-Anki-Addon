# [Background Auto Sync for Anki](https://github.com/athulkrishna2015/Background-Auto-Sync-for-Anki-Addon)

Automatically syncs your Anki collection in the background — without stealing focus, raising windows, or interrupting your workflow.

Install from anki [web](https://ankiweb.net/shared/info/226796325)

This addon is a fork of [Auto-Sync-Anki-Addon by Robin-Haupt-1](https://github.com/Robin-Haupt-1/Auto-Sync-Anki-Addon).

## Features

- **True background sync** — If Anki is minimized, it stays minimized. If another app has focus, Anki won't steal it. The sync happens silently.
- **Periodic sync** — Automatically syncs after a configurable period of inactivity (default: 1 minute after last interaction).
- **Idle periodic sync** — While you're away, keeps syncing periodically (default: Off) to pick up changes from AnkiWeb, mobile, or other devices.
- **Change detection** — Only syncs when the collection has actually been modified (cards added, reviewed, edited). Stops wasting bandwidth when nothing changed (enabled by default).
- **Idle-before-sync delay** — When a change is detected, waits for a configurable idle period before syncing, so it doesn't interrupt an active editing session (default: 2 minutes).
- **Interruption avoidance** — Three independently toggleable conditions (dialogs open / main window focused / reviewing) that defer sync, each with its own "allow sync anyway after" grace period, plus a global override timeout.
- **Session log file** — View a timestamped log in the Logs tab or inspect `auto_sync.log` in the add-on folder. The file is cleared when Anki starts so it contains the current session's activity.

## Important Considerations

- **Undo Queue:** Syncing terminates Anki's "undo" queue. Periodic sync may mean that if you take a break and return, you won't be able to undo actions performed just before the break.
- **Sync Conflicts:** Auto-syncing on one device while actively using, editing, or studying on another device can lead to sync conflicts.
- **Idle Periodic Sync:** Using "Idle periodic sync" while leaving Anki open may cause issues, especially if other add-ons with background activity are installed.
- **Interruption avoidance & override timeouts:** Each interruption condition defers sync while true, but the "allow sync anyway after" timeouts let a sync proceed once you've been idle long enough. Consider whether you want a sync to fire mid-review or with the browser open before raising these values.

## Installation

1. Download the latest `.ankiaddon` from [Releases](../../releases).
2. In Anki, go to **Tools → Add-ons → Install from file…** and select the downloaded file.
3. Restart Anki.

Or install via AnkiWeb addon code (226796325).

## Configuration

Go to **Tools → Background Auto Sync Options…** to configure. The options are organized into three sections on one scrollable Settings tab.

### Sync behavior

- **Only sync when changes are detected** *(Default: ✅ On)* — Sync only when the collection was modified, avoiding unnecessary network traffic when nothing changed.
- **Sync after** *(Default: 1 minute)* — Minutes of inactivity before syncing a changed collection. This control is disabled when change-only mode is enabled.
- **After a change, wait idle before syncing** *(Default: 2 minutes)* — After detecting a change, wait this long without user activity before syncing, so an active editing session is not interrupted. This is enabled when change-only mode is enabled.

### Interruption avoidance

These controls defer sync so it does not interrupt your work. Each condition can be enabled independently. A condition's effective grace period is the lower positive value of its specific timeout and the global timeout. A specific timeout of `Off` means it uses the global timeout; if both are `Off`, that condition never overrides.

- **Global override** *(Default: 10 minutes)* — Caps the grace period for all interruption conditions. For example, a global value of 10 minutes and a focus value of 5 minutes produces an effective focus grace of 5 minutes.
- **Avoid sync when dialogs are open** *(Default: ✅ On)* — Defer sync while selected Anki windows are open. The selectable windows are:
  - **Card browser** — the Browse window
  - **Add cards** — the Add Cards dialog
  - **Edit current card** — the Edit Current dialog
  - **Deck stats** — the statistics dialog
  - **Preferences** — the Preferences dialog
  - **Allow sync anyway after** *(Default: Off)* — Override this condition after the configured idle period.
- **Avoid sync when the main window is focused** *(Default: ✅ On)* — Defer sync while Anki is focused.
  - **Allow sync anyway after** *(Default: 5 minutes)* — Permit sync after the configured period of inactivity even if Anki remains focused.
- **Avoid sync while reviewing** *(Default: ✅ On)* — Defer sync unless Anki is on the deck browser or overview screen.
  - **Allow sync anyway after** *(Default: Off)* — Permit sync during another Anki screen after the configured period of inactivity.

### Background and network

- **When idle, sync every** *(Default: Off)* — While Anki is idle, periodically sync to pick up changes from AnkiWeb or another device. Use `Off` to disable. This is disabled when change-only mode is enabled.

- **Disable pre-sync internet check** *(Default: ❌ Off)* — Skip the connectivity check and immediately attempt to sync. This can help with restrictive firewalls.
- **On sync conflict** *(Default: Ask me each time)* — Choose how ambiguous full-sync conflicts are resolved: **Always AnkiWeb → local** discards local changes, while **Always local → AnkiWeb** overwrites AnkiWeb. Use a forced direction only when one side is authoritative.

Changes apply live. Use **Save** to close and keep them, **Cancel** to close the dialog, or **Reset Defaults** to restore the recommended defaults.

### Logs

The **Logs** tab shows timestamped sync activity from the current Anki session. The same entries are written to `auto_sync.log` in the add-on root. The file is truncated when Anki starts, making it useful for reviewing a reproducible bug without old sessions obscuring the output.
## Background Sync Behavior

The addon ensures syncs **never interrupt your work**:

- If Anki is **minimized** → stays minimized during and after sync
- If Anki is **behind other windows** → stays behind, doesn't raise to foreground
- If **another app** has focus → Anki won't steal focus
- Window state is saved before sync and restored after sync completes

## How It Works

1. After user activity in Anki, a countdown timer starts.
2. Once the idle timeout expires, the addon checks:
   - Is Anki in a "safe" state? (no dialogs open, not reviewing, etc.)
   - Is there internet connectivity?
   - If change-only mode: has the collection been modified?
3. Window state is saved (minimized? focused? background?).
4. Sync triggers via Anki's built-in sync.
5. After sync completes, window state is restored exactly.
6. The cycle restarts.

## Support

If you find this add-on useful, please consider supporting its development:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/D1D01W6NQT)

## License

GPL-3.0 — see [LICENSE.txt](LICENSE.txt).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full history of changes and releases.

- **Bug Fix:** Fixed a startup `NameError` crash due to missing configuration variables.
- **Documentation:** Major README refresh with explicit AnkiWeb installation instructions and UI behavior notes.
