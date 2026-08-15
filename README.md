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
- **Log window** — View a timestamped log of all sync activity for debugging.

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

Go to **Tools → Background Auto Sync Options…** to configure:

### Sync timing

- **Sync after** *(Default: 1 minute)* — Minutes of inactivity before triggering a sync. Disabled when **Only sync when changes detected** is On.
- **When idle, sync every** *(Default: Off)* — While Anki is idle (no activity), keep syncing every N minutes. Use 0/Off to disable periodic idle syncing. Disabled when **Only sync when changes detected** is On.
- **Only sync when changes detected** *(Default: ✅ On)* — Only sync when the collection was actually modified since the last sync. Avoids unnecessary network traffic when nothing changed.
- **Wait idle before syncing after change** *(Default: 2 minutes)* — After a change is detected, wait this long without user activity before syncing, so it doesn't interrupt an editing session.

### Interruption avoidance

These control *when* sync is deferred so it doesn't interrupt you. Each condition is independent; tick only the ones you care about. For each one, an **"Allow sync anyway after"** timeout lets a sync proceed anyway once you've been idle long enough (0 = Off / never override).

- **Global: allow sync anyway after** *(Default: 10 minutes)* — A global safety valve applied to all three conditions. For each condition the *effective* grace is the **lower** of its own timeout and this global value. So it acts as a cap: no matter what, a sync will go through once you've been idle this long.

- **Avoid sync when dialogs are open** *(Default: ✅ On)* — Defer sync while certain Anki windows are open. Use the sub-checkboxes to pick which windows count:
  - **Card browser** — the Browse window
  - **Add cards** — the Add/Edit cards window
  - **Edit current card** — inline card editor
  - **Deck stats** — deck statistics window
  - **Preferences** — preferences window
  - *(Allow sync anyway after — default: Off)* — when 0, sync always waits for these windows to close.

- **Avoid sync when the main window is focused** *(Default: ✅ On)* — Defer sync while the main Anki window has focus.
  - *(Allow sync anyway after — default: 5 minutes)* — if you leave Anki open and focused, a sync will still go through after 5 minutes of inactivity.

- **Avoid sync while reviewing** *(Default: ✅ On)* — Defer sync unless Anki is on the deck browser or overview screen (i.e. not mid-review).
  - *(Allow sync anyway after — default: Off)* — when 0, sync always waits until you're back on a safe screen. Raise it only if you're OK with a sync firing mid-review after that idle time.

### Network & conflicts

- **Disable pre-sync internet check** *(Default: ❌ Off)* — Skip the connectivity check and trigger the sync immediately (useful on extremely restrictive firewalls).
- **On sync conflict** *(Default: Ask me each time)* — Force a sync direction when a full-sync conflict occurs: **Always AnkiWeb → local** (discards local changes) or **Always local → AnkiWeb** (overwrites AnkiWeb). Use only if you have a single authoritative source.

*Tip: You can restore the optimal defaults at any time using the **Reset Defaults** button in the options menu.*
<img width="896" height="484" alt="Screenshot_20260326_194454" src="https://github.com/user-attachments/assets/8ffc01e1-c339-47c6-b764-ecf8ebeb0f5a" />

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


