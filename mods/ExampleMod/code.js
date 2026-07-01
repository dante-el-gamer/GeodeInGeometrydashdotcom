// =============================================================================
//  Codigo del Mod (code.js)
//  La logica principal del mod va ACA.
//
//  CONVENCIONES:
//    - Todo el codigo debe ir dentro de un IIFE: (function() { ... })();
//    - Usar `var` para variables internas (no contaminar el scope global).
//    - Los settings se leen desde `modSettingsValues["ExampleMod"]`.
//    - Para guardar estado usar: localStorage.setItem("mod-settings-ExampleMod", ...)
//    - Para recibir cambios en vivo usar window.__modOnSettings.
//    - Para cleanup usar window.__modCleanup.
// =============================================================================
(function() {
    "use strict";

    // -------------------------------------------------------------------------
    //  Leer settings desde el sistema.
    //  `modSettingsValues` es un objeto global claveado por IDname del mod.
    // -------------------------------------------------------------------------
    function getSettings() {
        if (typeof modSettingsValues !== "undefined" && modSettingsValues.ExampleMod) {
            return modSettingsValues.ExampleMod;
        }
        return {};
    }

    // -------------------------------------------------------------------------
    //  Leer un setting individual con fallback.
    // -------------------------------------------------------------------------
    function getSetting(key, fallback) {
        var s = getSettings();
        return s[key] !== undefined ? s[key] : fallback;
    }

    // -------------------------------------------------------------------------
    //  tick() - Se ejecuta cada ~300ms.
    //  Aca va la logica que necesita revisar el estado del juego periodicamente.
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
        // Ej: detectar cambios en la escena, modificar sprites, etc.
        //
        //  Referencias utiles:
        //    - window.__phaserGame  ->  Instancia del juego Phaser
        //    - game.scene.scenes[]  ->  Escenas activas
        //    - scene._player        ->  Jugador actual
        //    - scene._menuActive    ->  Si estamos en el menu principal
    }

    // -------------------------------------------------------------------------
    //  Hook de settings en vivo.
    //  Se llama cuando el usuario cambia un setting desde la UI.
    // -------------------------------------------------------------------------
    function onSettingsChange(modId) {
        if (modId !== "ExampleMod") return;
        // Reaccionar a cambios de settings sin esperar al proximo tick.
        // Ej: actualizar un texto, cambiar color, etc.
    }

    // -------------------------------------------------------------------------
    //  Hook de cleanup.
    //  Se llama cuando el mod se desactiva. RESTAURAR TODO.
    // -------------------------------------------------------------------------
    window.__modCleanup = function() {
        // Restaurar cualquier cambio que haya hecho el mod en el juego.
        // Si no se restaura, quedan modificaciones colgando.
    };

    // -------------------------------------------------------------------------
    //  Registrar hook de settings.
    // -------------------------------------------------------------------------
    window.__modApplySettings = onSettingsChange;
    if (!window.__modOnSettings) window.__modOnSettings = [];
    window.__modOnSettings.push(onSettingsChange);

    // -------------------------------------------------------------------------
    //  Iniciar el mod.
    // -------------------------------------------------------------------------
    tick();
    var pollTimer = setInterval(tick, 300);

    // -------------------------------------------------------------------------
    //  Si hacés un pollTimer, limpialo en cleanup.
    // -------------------------------------------------------------------------
    var origCleanup = window.__modCleanup;
    window.__modCleanup = function() {
        if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
        origCleanup();
    };
})();
