// =============================================================================
//  Mod Configuration (modConfig)
//  Cada mod DEBE tener un archivo Mod.js con una constante `modConfig`
//  que contenga la configuracion basica del mod.
// =============================================================================
const modConfig = {
    // -------------------------------------------------------------------------
    //  name        (string) - Nombre visible del mod en la lista.
    // -------------------------------------------------------------------------
    name: "Example Mod",

    // -------------------------------------------------------------------------
    //  IDname      (string) - Identificador interno (SIN espacios).
    //  Se usa para persistir settings, referencias en dependencias, etc.
    //  DEBE coincidir con el nombre de la carpeta del mod y con la entrada
    //  en mod-list.json.
    // -------------------------------------------------------------------------
    IDname: "ExampleMod",

    // -------------------------------------------------------------------------
    //  version     (string) - Version del mod (semver).
    // -------------------------------------------------------------------------
    version: "1.0.0",

    // -------------------------------------------------------------------------
    //  configurable (boolean) - Si el mod tiene settings (true) o no (false).
    //  Si es true, DEBE existir un archivo settings.js con la config.
    // -------------------------------------------------------------------------
    configurable: true,

    // -------------------------------------------------------------------------
    //  defaultEnabled (boolean) - Opcional. Si se activa solo al instalarlo.
    //  Por defecto es false. Si se pone true, el mod arranca activo sin que
    //  el usuario tenga que prenderlo manualmente.
    // -------------------------------------------------------------------------
    defaultEnabled: false,

    // -------------------------------------------------------------------------
    //  description (string) - Descripcion corta (se ve en la lista de mods).
    // -------------------------------------------------------------------------
    description: "Un mod de ejemplo para aprender a crear mods.",

    // -------------------------------------------------------------------------
    //  LongDescription (string) - Opcional. Descripcion larga (se ve en el
    //  detalle del mod). Soporta **Markdown basico**.
    // -------------------------------------------------------------------------
    LongDescription:
        "**Example Mod**\n\n" +
        "Este es un mod de ejemplo que muestra la estructura basica " +
        "que necesita cualquier mod para funcionar en el sistema.\n\n" +
        "**Camino de aprendizaje**\n\n" +
        "1. Leer Mod.js (configuracion basica)\n" +
        "2. Leer settings.js (tipos de settings disponibles)\n" +
        "3. Leer code.js (logica del mod)\n\n" +
        "**Recursos**\n\n" +
        "- Los assets van en `mods/ExampleMod/assets/`\n" +
        "- El icono del mod va en `mods/ExampleMod/icon.png`",

    // -------------------------------------------------------------------------
    //  developer (string) - Creador original del mod.
    // -------------------------------------------------------------------------
    developer: "danteelgamer_YT",

    // -------------------------------------------------------------------------
    //  PortDeveloper (string) - Opcional. Persona que porteo el mod.
    // -------------------------------------------------------------------------
    PortDeveloper: "",

    // -------------------------------------------------------------------------
    //  codeFiles (array de strings) - Opcional.
    //  Archivos JS adicionales en la carpeta code/ que se cargan DESPUES
    //  de code.js. Utiles para separar funcionalidad en modulos.
    //  Ej: ["utils.js", "ui.js", "network.js"]
    // -------------------------------------------------------------------------
    codeFiles: ["utils.js"],

    // -------------------------------------------------------------------------
    //  ItsOfficial (string) - Opcional. "YES" si es un mod oficial/firme.
    // -------------------------------------------------------------------------
    ItsOfficial: "NO"
};
