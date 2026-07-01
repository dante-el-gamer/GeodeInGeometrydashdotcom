[🇪🇸 **Español**](README_es.md)

![GeodeInGeometrydashDOTcom](READMEimg/GeodeInGeometrydashDOTcom.png)

**Geometry Dash running in the browser with mod support inspired by the [Geode SDK](https://geode-sdk.org/).**

A web port of the game that integrates a functional mod system with persistence, custom settings, live icon preview, and more. Built with **Phaser**, served as a static site.

---

## ✨ Features

- **24 official levels** included with music
- **Full mod system**: toggle on/off, configurable settings, dependencies
- **Mods overlay** with Geode SDK-styled UI
- **MoreIcons**: 485 cube icons with navigation, GD palette color picker, glow, custom URL icons, GD profile import
- **FPS Lock**: configurable FPS limiter (10-240)
- **Click Between Frames**: input capture between frames
- **MenuMusic**: custom menu music
- **Online level loading** via Cloudflare Workers + Service Worker
- **localStorage persistence** (active mods and settings)

---

## 🚀 How to Use

1. Open [GeodeInGeometrydash.com](https://GeodeInGeometrydash.com)
2. Click the mods icon (top right)
3. Toggle the mods you want
4. Each mod has its own settings panel

### URL Parameters

| Parameter | Description |
|-----------|-------------|
| `?id=` | Level ID |
| `?string=` | Level string (custom level) |
| `?songID=` | Song ID (default: 500476) |

---

## 🎮 Mods Included

| Mod | Version | Developer | Port |
|-----|---------|-----------|------|
| **ClickBetweenFrames** | 1.0.0 | syzzi | danteelgamer_YT |
| **ExampleMod** | 1.0.0 | danteelgamer_YT | — |
| **LockFPS** | 1.0.0 | danteelgamer_YT | — |
| **MoreIcons** | 1.0.0 | hiimjasmine00 | danteelgamer_YT |
| **MenuMusic** | 1.0.0 | danteelgamer_YT | — |
| **ProfileInMainMenu** | — | — | — |

---

## 🛠 How to Create a Mod

Each mod lives in `mods/<ID>/` and needs:

```
mods/<ID>/
├── Mod.js          # Mod config (name, version, developer, code)
├── settings.js     # Configurable settings (toggle, range, select, color, etc.)
├── code.js         # Mod logic (accesses the game loop via window.__phaserGame)
├── need.js         # (optional) Dependencies on other mods
├── icon.png        # (optional) Mod icon
└── assets/         # (optional) Additional resources
```

Available setting types: `toggle`, `range`, `text`, `number`, `select`, `color`, `gd-color`, `image-url`, `keybind`, `icon-grid`, `profile-import`.

Check the **ExampleMod** as a template to get started.

---

## 🧩 Available APIs for Mods

| API | Description |
|-----|-------------|
| `window.__game` | Central game API with events, accessors, and state detection |
| `window.__game.events` | EventEmitter: `on("game-ready")`, `on("player-spawn")`, `on("player-death")`, `on("menu")`, `on("gameplay")`, `on("pause")`, `on("resume")`, `on("level-complete")`, `on("update")` |
| `window.__game.getScene()` | Get the active game scene |
| `window.__game.getPlayer()` | Get the current player object (or null) |
| `window.__game.isInMenu()` | `true` if currently in the main menu |
| `window.__game.isPaused()` | `true` if the game is paused |
| `window.__game.getSettings(id)` | Get settings values for any mod |
| `window.__phaserGame` | Phaser.Game instance |
| `window.__fpsLimit` | FPS control (enable/disable/setTarget) |
| `window.__modOnSettings[]` | Settings callback array (push your handler) |
| `window.__modCleanup` | Cleanup array (push your cleanup functions) |
| `window.__getSettings(id)` | Global settings helper |
| `localStorage` | Persistence |

---

## 📦 Project Structure

```
GeodeInGeometrydash.com/
├── index.html           # Entry point + mod system + game canvas
├── worker.js            # Service Worker (levels + music proxy)
├── favicon.ico
├── assets/              # Phaser game engine, spritesheets, levels, music
├── GeodeAssets/         # Geode UI resources (spritesheets, fonts, sounds)
├── Icons/               # 677 GD icons (cube, ship, ball)
├── mods/                # Installed mods
├── font/                # Pusab font
├── READMEimg/           # README images
└── *.py                 # Asset processing tools
```

---

## 🌐 Infrastructure

- **Phaser** (game engine)
- **Cloudflare Workers** (level and song proxy):
  - `getleveldata.lasokar.workers.dev`
  - `getlevelsong.lasokar.workers.dev`
  - `fetchsongid.lasokar.workers.dev`
- **Service Worker** for request interception
- **No build step** — pure static site

---

## 📄 Licenses

- **Geode SDK**: BSL v1.0 (Business Source License)
- **MoreIcons**: MIT License (by hiimjasmine00)
- **Rest of the project**: contact the author

---

## 👤 Author

**[danteelgamer_YT](https://youtube.com/@danteelgameryt)**

- YouTube: https://youtube.com/@danteelgameryt
- GitHub: https://github.com/dante-el-gamer
- Web: https://dante-el-gamer.github.io/

---

## 🙏 Credits

- **Geode Team**: HJfod, Alk1m123, Mat, ConfiG, Cvolton, Camila314, zmx, PoweredByPie, fig, FireCubez and [contributors](https://github.com/geode-sdk/geode/graphs/contributors)
- **RobTop Games** for Geometry Dash
- **hiimjasmine00** for the original MoreIcons mod
- **syzzi** for the original Click Between Frames
- **lasokar** for the Cloudflare Workers proxy
