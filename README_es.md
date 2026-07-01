![GeodeInGeometrydashDOTcom](READMEimg/GeodeInGeometrydashDOTcom.png)

[🇬🇧 **English**](README.md)

**Geometry Dash corriendo en el navegador con soporte de mods inspirado en el [Geode SDK](https://geode-sdk.org/).**

Un port web del juego que integra un sistema de mods funcional con persistencia, settings custom, preview de iconos en vivo y más. Construido con **Phaser**, servido como sitio estático.

---

## ✨ Features

- **24 niveles oficiales** incluidos con música
- **Sistema de mods completo**: toggle on/off, settings configurables, dependencias
- **Overlay de mods** con UI estilizada al Geode SDK
- **MoreIcons**: 485 iconos de cubo navegables, color picker con paleta GD, glow, iconos custom por URL, importación desde perfil real de GD
- **FPS Lock**: limitador de FPS configurable (10-240)
- **Click Between Frames**: captura inputs entre frames
- **MenuMusic**: música personalizada en el menú principal
- **Carga de niveles online** via Cloudflare Workers + Service Worker
- **Persistencia en localStorage** (mods activos y settings)

---

## 🚀 Cómo usar

1. Abrí [GeodeInGeometrydash.com](https://GeodeInGeometrydash.com)
2. Hacé click en el ícono de mods (arriba a la derecha)
3. Activá los mods que quieras
4. Cada mod tiene su propio panel de settings

### Parámetros de URL

| Parámetro | Descripción |
|-----------|-------------|
| `?id=` | ID del nivel |
| `?string=` | Level string (nivel custom) |
| `?songID=` | ID de la canción (default: 500476) |

---

## 🎮 Mods incluidos

| Mod | Versión | Creador | Port |
|-----|---------|-----------|------|
| **ClickBetweenFrames** | 1.0.0 | syzzi | danteelgamer_YT |
| **ExampleMod** | 1.0.0 | danteelgamer_YT | — |
| **LockFPS** | 1.0.0 | danteelgamer_YT | — |
| **MoreIcons** | 1.0.0 | hiimjasmine00 | danteelgamer_YT |
| **MenuMusic** | 1.0.0 | danteelgamer_YT | — |
| **ProfileInMainMenu** | — | — | — |

---

## 🛠 Cómo crear un mod

Cada mod vive en `mods/<ID>/` y necesita:

```
mods/<ID>/
├── Mod.js          # Config del mod (nombre, versión, developer, código)
├── settings.js     # Settings configurables (toggle, range, select, color, etc.)
├── code.js         # Lógica del mod (accede al game loop via window.__phaserGame)
├── need.js         # (opcional) Dependencias de otros mods
├── icon.png        # (opcional) Icono del mod
└── assets/         # (opcional) Recursos adicionales
```

Tipos de settings disponibles: `toggle`, `range`, `text`, `number`, `select`, `color`, `gd-color`, `image-url`, `keybind`, `icon-grid`, `profile-import`.

Mirá el **ExampleMod** como template para arrancar.

---

## 🧩 APIs disponibles para mods

| API | Descripción |
|-----|-------------|
| `window.__game` | API central con eventos, accessors y detección de estado |
| `window.__game.events` | EventEmitter: `on("game-ready")`, `on("player-spawn")`, `on("player-death")`, `on("menu")`, `on("gameplay")`, `on("pause")`, `on("resume")`, `on("level-complete")`, `on("update")` |
| `window.__game.getScene()` | Obtiene la escena activa del juego |
| `window.__game.getPlayer()` | Obtiene el jugador actual (o null) |
| `window.__game.isInMenu()` | `true` si está en el menú principal |
| `window.__game.isPaused()` | `true` si el juego está pausado |
| `window.__game.getSettings(id)` | Obtiene los settings de cualquier mod |
| `window.__phaserGame` | Instancia de Phaser.Game |
| `window.__fpsLimit` | Control de FPS (enable/disable/setTarget) |
| `window.__modOnSettings[]` | Array de callbacks de settings |
| `window.__modCleanup` | Array de cleanup (push tus funciones acá) |
| `window.__getSettings(id)` | Helper global de settings |
| `localStorage` | Persistencia |

---

## 📦 Estructura del proyecto

```
GeodeInGeometrydash.com/
├── index.html           # Entry point + mod system + game canvas
├── worker.js            # Service Worker (levels + music proxy)
├── favicon.ico
├── assets/              # Phaser game engine, spritesheets, niveles, música
├── GeodeAssets/         # Geode UI resources (spritesheets, fonts, sounds)
├── Icons/               # 677 iconos GD (cube, ship, ball)
├── mods/                # Mods instalados
├── font/                # Pusab font
├── READMEimg/           # Imágenes para el README
└── *.py                 # Herramientas de procesamiento de assets
```

---

## 🌐 Infraestructura

- **Phaser** (game engine)
- **Cloudflare Workers** (proxy de niveles y canciones):
  - `getleveldata.lasokar.workers.dev`
  - `getlevelsong.lasokar.workers.dev`
  - `fetchsongid.lasokar.workers.dev`
- **Service Worker** para intercepción de requests
- **Sin build step** — sitio estático puro

---

## 📄 Licencias

- **Geode SDK**: BSL v1.0 (Business Source License)
- **MoreIcons**: MIT License (por hiimjasmine00)
- **Resto del proyecto**: consultar con el autor

---

## 👤 Autor

**[danteelgamer_YT](https://youtube.com/@danteelgameryt)**

- YouTube: https://youtube.com/@danteelgameryt
- GitHub: https://github.com/dante-el-gamer
- Web: https://dante-el-gamer.github.io/

---

## 🙏 Créditos

- **Geode Team**: HJfod, Alk1m123, Mat, ConfiG, Cvolton, Camila314, zmx, PoweredByPie, fig, FireCubez y [contribuyentes](https://github.com/geode-sdk/geode/graphs/contributors)
- **RobTop Games** por Geometry Dash
- **hiimjasmine00** por el mod MoreIcons original
- **syzzi** por Click Between Frames original
- **lasokar** por los Cloudflare Workers de proxy
