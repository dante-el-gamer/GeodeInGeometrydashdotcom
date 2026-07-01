// =============================================================================
//  Modulo: utils.js
//  Los archivos en code/ se cargan DESPUES de code.js.
//  Pueden depender de variables/funciones definidas en code.js.
//
//  CONVENCIONES:
//    - Usar un objeto namespace para no contaminar el scope global.
//    - Ej: window.ExampleModUtils = { ... }
// =============================================================================
(function() {
    "use strict";

    // -------------------------------------------------------------------------
    //  Ejemplo: funcion de utilidad para leer settings.
    //  code.js ya tiene su propia version, pero esta muestra como
    //  organizar codigo auxiliar en modulos separados.
    // -------------------------------------------------------------------------
    window.ExampleModUtils = {
        getSetting: function(key, fallback) {
            if (typeof modSettingsValues !== "undefined" && modSettingsValues.ExampleMod) {
                return modSettingsValues.ExampleMod[key] !== undefined
                    ? modSettingsValues.ExampleMod[key]
                    : fallback;
            }
            return fallback;
        },

        log: function(msg) {
            if (this.getSetting("debug", false)) {
                console.log("[ExampleMod]", msg);
            }
        },

        formatTime: function(ms) {
            var s = Math.floor(ms / 1000);
            var m = Math.floor(s / 60);
            s = s % 60;
            return m + ":" + (s < 10 ? "0" : "") + s;
        }
    };
})();
