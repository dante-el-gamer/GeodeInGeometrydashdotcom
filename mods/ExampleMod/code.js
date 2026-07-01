// =============================================================================
//  Codigo del Mod (code.js)
//  La logica principal del mod va ACA.
//
//  CONVENCIONES:
//    - Todo el codigo debe ir dentro de un IIFE: (function() { ... })();
//    - Usar `var` para variables internas (no contaminar el scope global).
//    - Los settings se leen via `__game.getSettings("ExampleMod")`.
//    - Para recibir cambios en vivo usar `window.__modOnSettings.push(fn)`.
//    - Para cleanup usar `window.__modCleanup.push(function() { ... })`.
// =============================================================================
(function() {
    "use strict";

    // -------------------------------------------------------------------------
    //  Leer settings desde el sistema.
    //  `__game.getSettings(modId)` devuelve el objeto de settings o null.
    // -------------------------------------------------------------------------
    function getSettings() {
        return window.__game ? window.__game.getSettings("ExampleMod") : null;
    }

    // -------------------------------------------------------------------------
    //  Leer un setting individual con fallback.
    // -------------------------------------------------------------------------
    function getSetting(key, fallback) {
        var s = getSettings();
        return s && s[key] !== undefined ? s[key] : fallback;
    }

    // -------------------------------------------------------------------------
    //  En vez de polling con setInterval, podés escuchar eventos:
    //
    //    window.__game.events.on("game-ready", function() { ... });
    //    window.__game.events.on("gameplay", function() { ... });
    //    window.__game.events.on("menu", function() { ... });
    //    window.__game.events.on("player-spawn", function(player) { ... });
    //    window.__game.events.on("player-death", function() { ... });
    //    window.__game.events.on("level-complete", function() { ... });
    //    window.__game.events.on("pause", function() { ... });
    //    window.__game.events.on("resume", function() { ... });
    //    window.__game.events.on("scene-change", function(scene) { ... });
    //    window.__game.events.on("update", function() { ... });
    //
    //  O todavía podés usar el patron de polling clasico con setInterval.
    //  Si usas eventos, no necesitas el timer.
    // -------------------------------------------------------------------------
    function tick() {
        var enabled = getSetting("enabled", true);
        if (!enabled) return;

        var speed = getSetting("speed", 50);
        var text = getSetting("displayText", "Hello GD!");
        var theme = getSetting("theme", "dark");
        var color = getSetting("highlightColor", "#ff8800");
        var key = getSetting("toggleKey", "P");

        // --- TU CODIGO ACA ---
        // Referencias utiles via window.__game:
        //   __game.getScene()       ->  Escena activa del juego
        //   __game.getPlayer()      ->  Jugador actual (o null)
        //   __game.isInMenu()       ->  true si estamos en el menu
        //   __game.isPaused()       ->  true si el juego esta pausado
        //   __game.getSettings(id)  ->  Settings de cualquier mod
        //
        // Acceso directo (game API):
        //   window.__phaserGame     ->  Instancia del juego Phaser
        //   scene._player           ->  Objeto del jugador
        //   scene._menuActive       ->  Bool: menu activo
    }

    // -------------------------------------------------------------------------
    //  Hook de settings en vivo.
    // -------------------------------------------------------------------------
    function onSettingsChange(modId) {
        if (modId !== "ExampleMod") return;
    }

    // -------------------------------------------------------------------------
    //  Cleanup: ahora podés pushear funciones al array.
    //  Todas se ejecutan cuando se desactiva el mod.
    // -------------------------------------------------------------------------
    if (!window.__modCleanup) window.__modCleanup = [];
    window.__modCleanup.push(function() {
        if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
    });

    // -------------------------------------------------------------------------
    //  Registrar hook de settings.
    // -------------------------------------------------------------------------
    window.__modApplySettings = onSettingsChange;
    if (!window.__modOnSettings) window.__modOnSettings = [];
    window.__modOnSettings.push(onSettingsChange);

    // -------------------------------------------------------------------------
    //  Iniciar el mod (con polling clasico como ejemplo).
    //  Si usas eventos de __game, no necesitas esto.
    // -------------------------------------------------------------------------
    tick();
    var pollTimer = setInterval(tick, 300);
})();
