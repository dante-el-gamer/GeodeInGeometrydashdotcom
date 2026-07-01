// =============================================================================
//  Mod Settings (modSettings)
//  Array de objetos que definen las opciones configurables del mod.
//  Cada setting tiene un `type` que determina como se renderiza en la UI.
//  Tipos disponibles:
//    - "toggle"       : Switch on/off
//    - "range"        : Slider numerico (min, max, step)
//    - "text"         : Campo de texto libre
//    - "number"       : Campo numerico
//    - "select"       : Dropdown (requiere `options: [{label, value}]`)
//    - "color"        : Color picker (hex)
//    - "gd-color"     : Color picker con paleta de Geometry Dash
//    - "image-url"    : Campo para URL de imagen con preview
//    - "keybind"      : Captura de tecla
//    - "icon-grid"    : Grilla de iconos (requiere iconBase, iconExt, count)
//    - "profile-import": Importar perfil desde GD (requiere targets)
// =============================================================================
const modSettings = [
    // -------------------------------------------------------------------------
    //  toggle - Interruptor de encendido/apagado.
    // -------------------------------------------------------------------------
    {
        key: "enabled",         // Clave unica para guardar/leer el valor
        label: "Mod enabled",   // Texto visible en la UI
        type: "toggle",         // Tipo de control
        default: true,          // Valor por defecto
        hint: "Enable or disable the mod functionality."  // Texto de ayuda
    },

    // -------------------------------------------------------------------------
    //  range - Slider para valores numericos continuos.
    // -------------------------------------------------------------------------
    {
        key: "speed",
        label: "Speed",
        type: "range",
        default: 50,
        min: 0,                 // Valor minimo
        max: 100,               // Valor maximo
        step: 1,                // Incremento por paso
        hint: "How fast does the thing go? (0-100)"
    },

    // -------------------------------------------------------------------------
    //  text - Campo de texto libre (una linea).
    // -------------------------------------------------------------------------
    {
        key: "displayText",
        label: "Display text",
        type: "text",
        default: "Hello GD!",
        hint: "Text to show on screen."
    },

    // -------------------------------------------------------------------------
    //  select - Menu desplegable con opciones predefinidas.
    // -------------------------------------------------------------------------
    {
        key: "theme",
        label: "Theme",
        type: "select",
        default: "dark",
        options: [              // Array de opciones {label, value}
            { label: "Dark", value: "dark" },
            { label: "Light", value: "light" },
            { label: "GD Default", value: "gd" }
        ],
        hint: "Pick a color theme."
    },

    // -------------------------------------------------------------------------
    //  color - Selector de color en formato HEX.
    // -------------------------------------------------------------------------
    {
        key: "highlightColor",
        label: "Highlight color",
        type: "color",
        default: "#ff8800",
        hint: "Color for highlights (hex format)."
    },

    // -------------------------------------------------------------------------
    //  keybind - Captura de combinacion de teclas.
    // -------------------------------------------------------------------------
    {
        key: "toggleKey",
        label: "Toggle keybind",
        type: "keybind",
        default: "P",
        hint: "Press a key to toggle the mod feature."
    }
];
