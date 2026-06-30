(function() {
    var audio = null;
    var pollTimer = null;
    var wasInMenu = false;

    function getVolume() {
        if (typeof modSettingsValues !== 'undefined' && modSettingsValues.MenuMusic) {
            return (modSettingsValues.MenuMusic.volume || 90) / 100;
        }
        return 0.5;
    }

    function isInMenu() {
        var game = window.__phaserGame;
        if (!game || !game.scene) return false;
        var scenes = game.scene.scenes;
        for (var i = 0; i < scenes.length; i++) {
            if (scenes[i]._menuActive === true) return true;
        }
        return false;
    }

    function initAudio() {
        if (audio) return;
        audio = new Audio('mods/MenuMusic/assets/music/MainMenu.mp3');
        audio.loop = true;
        audio.volume = getVolume();
    }

    function tick() {
        var inMenu = isInMenu();
        if (inMenu === wasInMenu) return;
        wasInMenu = inMenu;

        initAudio();
        if (inMenu) {
            audio.currentTime = 0;
            audio.play().catch(function() {});
        } else {
            audio.pause();
        }
    }

    function onSettings(modId) {
        if (modId === 'MenuMusic' && audio) {
            audio.volume = getVolume();
        }
    }

    tick();
    pollTimer = setInterval(tick, 300);

    window.__modCleanup = function() {
        if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
        if (audio) { audio.pause(); audio = null; }
    };

    window.__modApplySettings = onSettings;
    if (!window.__modOnSettings) window.__modOnSettings = [];
    window.__modOnSettings.push(onSettings);
})();
