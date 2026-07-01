(function() {
    var currentIcon = null;
    var currentColor1 = null;
    var currentColor2 = null;
    var currentGlow = false;
    var currentCustomUrl = null;
    var pollTimer = null;
    var lastPlayer = null;

    var ORIG_FRAME_W = 61;
    var ORIG_FRAME_H = 60;

    var DEFAULT_COLOR_1 = '#ffffff';
    var DEFAULT_COLOR_2 = '#000000';

    function getScene() {
        var game = window.__phaserGame;
        if (!game || !game.scene) return null;
        var scenes = game.scene.scenes;
        for (var i = 0; i < scenes.length; i++) {
            if (scenes[i]._player) return scenes[i];
        }
        return scenes[0] || null;
    }

    function getTexMan(scene) {
        return scene && scene.sys && scene.sys.textures;
    }

    function getMainMenuScene() {
        var game = window.__phaserGame;
        if (!game || !game.scene) return null;
        var scenes = game.scene.scenes;
        for (var i = 0; i < scenes.length; i++) {
            if (scenes[i]._menuActive !== undefined) return scenes[i];
        }
        return null;
    }

    function hexEquals(a, b) {
        return (a || '').toLowerCase() === (b || '').toLowerCase();
    }

    function hexToRgb(hex) {
        var v = parseInt(hex.slice(1), 16);
        return { r: (v >> 16) & 0xff, g: (v >> 8) & 0xff, b: v & 0xff };
    }

    function recolorIcon(img, color1, color2) {
        var isDefault = hexEquals(color1, DEFAULT_COLOR_1) && hexEquals(color2, DEFAULT_COLOR_2);
        var canvas = document.createElement('canvas');
        canvas.width = ORIG_FRAME_W;
        canvas.height = ORIG_FRAME_H;
        var ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, ORIG_FRAME_W, ORIG_FRAME_H);
        if (isDefault) return canvas;

        var c1 = hexToRgb(color1 || DEFAULT_COLOR_1);
        var c2 = hexToRgb(color2 || DEFAULT_COLOR_2);
        var imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        var d = imageData.data;

        for (var i = 0; i < d.length; i += 4) {
            var r = d[i], g = d[i + 1], b = d[i + 2];
            if (d[i + 3] === 0) continue;
            if (r < 25 && g < 25 && b < 25) continue;
            var lum = (r * 0.299 + g * 0.587 + b * 0.114) / 255;
            var t = Math.min(1, Math.max(0, (lum - 0.12) / 0.88));
            d[i]     = Math.round(c1.r * t + c2.r * (1 - t));
            d[i + 1] = Math.round(c1.g * t + c2.g * (1 - t));
            d[i + 2] = Math.round(c1.b * t + c2.b * (1 - t));
        }
        ctx.putImageData(imageData, 0, 0);
        return canvas;
    }

    function updateGlow(scene, player) {
        if (!player) return;
        var shouldGlow = currentGlow && currentColor1 && currentColor2;
        if (player._playerGlowLayer && player._playerGlowLayer.sprite) {
            player._playerGlowLayer.sprite.setVisible(!!shouldGlow);
            if (shouldGlow && currentColor2) {
                var c = hexToRgb(currentColor2);
                player._playerGlowLayer.sprite.setTint((c.r << 16) | (c.g << 8) | c.b);
            }
        }
        if (player._playerOverlayLayer && player._playerOverlayLayer.sprite) {
            player._playerOverlayLayer.sprite.setVisible(!shouldGlow);
        }
    }

    function applyIcon(scene, player, iconNum, color1, color2, glow, customUrl) {
        if (!player || !player._playerSpriteLayer || !player._playerSpriteLayer.sprite) return;
        var spr = player._playerSpriteLayer.sprite;
        if (!spr.scene) return;

        currentGlow = !!glow;

        var img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = function() {
            var texMan = getTexMan(scene);
            if (!texMan) return;

            var key;
            if (customUrl) {
                key = 'mic_custom_' + customUrl;
                var canvas = document.createElement('canvas');
                canvas.width = ORIG_FRAME_W;
                canvas.height = ORIG_FRAME_H;
                var ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, ORIG_FRAME_W, ORIG_FRAME_H);
                if (!texMan.exists(key)) texMan.addCanvas(key, canvas);
            } else {
                var canvas = recolorIcon(img, color1 || currentColor1, color2 || currentColor2);
                key = 'mic_' + iconNum + '_' + (color1 || currentColor1) + '_' + (color2 || currentColor2);
                if (!texMan.exists(key)) texMan.addCanvas(key, canvas);
            }

            spr.setTexture(key);
            spr.setTint(0xffffff);
            spr.setDisplaySize(ORIG_FRAME_W, ORIG_FRAME_H);
            updateGlow(scene, player);
        };
        img.onerror = function() { console.warn('[MoreIcons] Failed loading icon', iconNum, customUrl); };
        img.src = customUrl || ('Icons/cube/cube_' + iconNum + '.png');
    }

    function restoreIcon(scene, player) {
        if (!player || !player._playerSpriteLayer || !player._playerSpriteLayer.sprite) return;
        var spr = player._playerSpriteLayer.sprite;
        spr.setTexture('GJ_WebSheet', 'player_01_001.png');
        spr.setDisplaySize(ORIG_FRAME_W, ORIG_FRAME_H);
        var pr = window.bgr, pg = window.bgg, pb = window.bgb;
        spr.setTint(((pr || 255) << 16) | ((pg || 255) << 8) | (pb || 255));

        if (player._playerOverlayLayer && player._playerOverlayLayer.sprite) {
            player._playerOverlayLayer.sprite.setVisible(true);
            var sr = window.gr, sg = window.gg, sb = window.gb;
            player._playerOverlayLayer.sprite.setTint(((sr || 255) << 16) | ((sg || 255) << 8) | (sb || 255));
        }
        if (player._playerGlowLayer && player._playerGlowLayer.sprite) {
            player._playerGlowLayer.sprite.setVisible(!!player._playerGlowLayer.sprite._glowEnabled);
        }
    }

    function moreIconsOnSettings(modId, settings) {
        if (modId !== 'MoreIcons') return;
        var changed = false;
        if (settings.cubeIcon !== undefined) { currentIcon = settings.cubeIcon; changed = true; }
        if (settings.color1 !== undefined) { currentColor1 = settings.color1; changed = true; }
        if (settings.color2 !== undefined) { currentColor2 = settings.color2; changed = true; }
        if (settings.glow !== undefined) { currentGlow = settings.glow; changed = true; }
        if (settings.customIcon !== undefined) { currentCustomUrl = settings.customIcon; changed = true; }
        if (changed) {
            var scene = getScene();
            if (scene && scene._player && currentIcon !== null) {
                applyIcon(scene, scene._player, currentIcon, currentColor1, currentColor2, currentGlow, currentCustomUrl);
            }
        }
    }
    window.__modApplySettings = moreIconsOnSettings;
    if (!window.__modOnSettings) window.__modOnSettings = [];
    window.__modOnSettings.push(moreIconsOnSettings);

    try {
        var saved = JSON.parse(localStorage.getItem('mod-settings-MoreIcons') || '{}');
        currentIcon = saved.cubeIcon || 1;
        currentColor1 = saved.color1 || DEFAULT_COLOR_1;
        currentColor2 = saved.color2 || DEFAULT_COLOR_2;
        currentGlow = saved.glow === true;
        currentCustomUrl = saved.customIcon || null;
    } catch(e) {
        currentIcon = 1;
        currentColor1 = DEFAULT_COLOR_1;
        currentColor2 = DEFAULT_COLOR_2;
        currentGlow = false;
        currentCustomUrl = null;
    }

    function tick() {
        var scene = getScene();
        if (!scene) return;
        var player = scene._player;
        if (player && player !== lastPlayer) {
            lastPlayer = player;
            if (currentIcon !== null) {
                applyIcon(scene, player, currentIcon, currentColor1, currentColor2, currentGlow, currentCustomUrl);
            }
        }
        if (!player) lastPlayer = null;
    }

    // ── Export shared API for code/SkinMenu/ ────────────────────
    window.__moreIcons = {
        currentIcon: currentIcon,
        currentColor1: currentColor1,
        currentColor2: currentColor2,
        currentGlow: currentGlow,
        currentCustomUrl: currentCustomUrl,
        ORIG_FRAME_W: ORIG_FRAME_W,
        ORIG_FRAME_H: ORIG_FRAME_H,
        DEFAULT_COLOR_1: DEFAULT_COLOR_1,
        DEFAULT_COLOR_2: DEFAULT_COLOR_2,
        getScene: getScene,
        getTexMan: getTexMan,
        getMainMenuScene: getMainMenuScene,
        recolorIcon: recolorIcon,
        applyIcon: applyIcon,
        restoreIcon: restoreIcon,
        getSettings: function() {
            return { icon: currentIcon, color1: currentColor1, color2: currentColor2, glow: currentGlow, customUrl: currentCustomUrl };
        },
        onTick: []
    };

    // Make color/icon vars writable from menu code via __moreIcons
    function syncState() {
        currentIcon = window.__moreIcons.currentIcon;
        currentColor1 = window.__moreIcons.currentColor1;
        currentColor2 = window.__moreIcons.currentColor2;
        currentGlow = window.__moreIcons.currentGlow;
        currentCustomUrl = window.__moreIcons.currentCustomUrl;
    }

    var origTick = tick;
    tick = function() {
        origTick();
        syncState();
        for (var i = 0; i < window.__moreIcons.onTick.length; i++) {
            window.__moreIcons.onTick[i]();
        }
    };

    tick();
    pollTimer = setInterval(tick, 300);

    window.__modCleanup = function() {
        if (window.__moreIcons.cleanup) window.__moreIcons.cleanup();
        if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
        currentIcon = null;
        lastPlayer = null;
        var scene = getScene();
        if (scene && scene._player) restoreIcon(scene, scene._player);
    };
})();
