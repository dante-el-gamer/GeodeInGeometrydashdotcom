(function() {
    var currentIcon = null;
    var currentColor1 = null;
    var currentColor2 = null;
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
            // preserve true black outlines (all channels very low)
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

    function applyIcon(scene, player, iconNum, color1, color2) {
        if (!player || !player._playerSpriteLayer || !player._playerSpriteLayer.sprite) return;
        var spr = player._playerSpriteLayer.sprite;
        if (!spr.scene) return;

        var img = new Image();
        img.onload = function() {
            var canvas = recolorIcon(img, color1 || currentColor1, color2 || currentColor2);
            var texMan = getTexMan(scene);
            if (!texMan) return;

            var key = 'mic_' + iconNum + '_' + (color1 || currentColor1) + '_' + (color2 || currentColor2);
            if (!texMan.exists(key)) texMan.addCanvas(key, canvas);

            spr.setTexture(key);
            spr.setTint(0xffffff);
            spr.setDisplaySize(ORIG_FRAME_W, ORIG_FRAME_H);
            if (player._playerOverlayLayer && player._playerOverlayLayer.sprite) {
                player._playerOverlayLayer.sprite.setVisible(false);
            }
            if (player._playerGlowLayer && player._playerGlowLayer.sprite) {
                player._playerGlowLayer.sprite.setVisible(false);
            }
        };
        img.onerror = function() { console.warn('[MoreIcons] Failed loading icon', iconNum); };
        img.src = 'Icons/cube/cube_' + iconNum + '.png';
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

    window.__modApplySettings = function(modId, settings) {
        if (modId !== 'MoreIcons') return;
        var changed = false;
        if (settings.cubeIcon !== undefined) { currentIcon = settings.cubeIcon; changed = true; }
        if (settings.color1 !== undefined) { currentColor1 = settings.color1; changed = true; }
        if (settings.color2 !== undefined) { currentColor2 = settings.color2; changed = true; }
        if (changed) {
            var scene = getScene();
            if (scene && scene._player && currentIcon !== null) {
                applyIcon(scene, scene._player, currentIcon, currentColor1, currentColor2);
            }
        }
    };

    try {
        var saved = JSON.parse(localStorage.getItem('mod-settings-MoreIcons') || '{}');
        currentIcon = saved.cubeIcon || 1;
        currentColor1 = saved.color1 || DEFAULT_COLOR_1;
        currentColor2 = saved.color2 || DEFAULT_COLOR_2;
    } catch(e) {
        currentIcon = 1;
        currentColor1 = DEFAULT_COLOR_1;
        currentColor2 = DEFAULT_COLOR_2;
    }

    function tick() {
        var scene = getScene();
        if (!scene) return;
        var player = scene._player;
        if (player && player !== lastPlayer) {
            lastPlayer = player;
            if (currentIcon !== null) {
                applyIcon(scene, player, currentIcon, currentColor1, currentColor2);
            }
        }
        if (!player) lastPlayer = null;
    }

    tick();
    pollTimer = setInterval(tick, 300);

    window.__modCleanup = function() {
        if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
        currentIcon = null;
        lastPlayer = null;
        var scene = getScene();
        if (scene && scene._player) restoreIcon(scene, scene._player);
    };
})();
