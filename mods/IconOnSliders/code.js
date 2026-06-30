(function() {
    var animEnabled = true;
    var pollTimer = null;

    var texKeyNormal = null;
    var texKeySelected = null;
    var loadingTexture = false;

    var CANVAS_SIZE = 76;

    function getScenes() {
        var game = window.__phaserGame;
        if (!game || !game.scene) return [];
        return game.scene.scenes || [];
    }

    function forEachScene(fn) {
        var scenes = getScenes();
        for (var s = 0; s < scenes.length; s++) {
            if (scenes[s] && scenes[s].children) fn(scenes[s]);
        }
    }

    function getTexMan(scene) {
        return scene && scene.sys && scene.sys.textures;
    }

    function getFirstTexMan() {
        var scenes = getScenes();
        for (var s = 0; s < scenes.length; s++) {
            var tm = getTexMan(scenes[s]);
            if (tm) return { texMan: tm, scene: scenes[s] };
        }
        return null;
    }

    function getMI() {
        return window.__moreIcons;
    }

    function getIconNum() {
        var s = modSettingsValues && modSettingsValues.MoreIcons;
        return (s && s.cubeIcon) || 1;
    }

    function getColor1() {
        var s = modSettingsValues && modSettingsValues.MoreIcons;
        return (s && s.color1) || '#ffffff';
    }

    function getColor2() {
        var s = modSettingsValues && modSettingsValues.MoreIcons;
        return (s && s.color2) || '#000000';
    }

    function ensureIconTextures() {
        var found = getFirstTexMan();
        if (!found) return false;
        var texMan = found.texMan;
        var scene = found.scene;

        var iconNum = getIconNum();
        var c1 = getColor1();
        var c2 = getColor2();

        var normalKey = 'ios_' + iconNum + '_' + c1 + '_' + c2;
        var selKey = normalKey + '_sel';

        if (texMan.exists(normalKey)) {
            texKeyNormal = normalKey;
            texKeySelected = selKey;
            return true;
        }

        if (loadingTexture) return false;
        loadingTexture = true;

        var baseScale = Math.min(CANVAS_SIZE / 61, CANVAS_SIZE / 60);

        var img = new Image();
        img.onload = function() {
            var mi = getMI();
            if (!mi) {
                loadingTexture = false;
                return;
            }
            var canvas = mi.recolorIcon(img, c1, c2);

            var pad = 0.88;
            var s = baseScale * pad;
            var iw = Math.round(61 * s);
            var ih = Math.round(60 * s);
            var ix = Math.round((CANVAS_SIZE - iw) / 2);
            var iy = Math.round((CANVAS_SIZE - ih) / 2);

            var c1c = document.createElement('canvas');
            c1c.width = CANVAS_SIZE; c1c.height = CANVAS_SIZE;
            var ctx1 = c1c.getContext('2d');
            ctx1.drawImage(canvas, ix, iy, iw, ih);
            if (!texMan.exists(normalKey)) texMan.addCanvas(normalKey, c1c);

            var padSel = 0.96;
            var s2 = baseScale * padSel;
            var iw2 = Math.round(61 * s2);
            var ih2 = Math.round(60 * s2);
            var ix2 = Math.round((CANVAS_SIZE - iw2) / 2);
            var iy2 = Math.round((CANVAS_SIZE - ih2) / 2);
            var c2c = document.createElement('canvas');
            c2c.width = CANVAS_SIZE; c2c.height = CANVAS_SIZE;
            var ctx2 = c2c.getContext('2d');
            ctx2.drawImage(canvas, ix2, iy2, iw2, ih2);
            if (!texMan.exists(selKey)) texMan.addCanvas(selKey, c2c);

            texKeyNormal = normalKey;
            texKeySelected = selKey;
            loadingTexture = false;

            applyToAll(scene);
        };
        img.onerror = function() {
            console.warn('[IconOnSliders] Failed loading icon', iconNum);
            loadingTexture = false;
        };
        img.src = 'Icons/cube/cube_' + iconNum + '.png';
        return false;
    }

    function isSliderThumb(child) {
        if (!child || child.type !== 'Image') return false;
        if (!child.texture) return false;
        if (child.texture.key === 'GJ_WebSheet') {
            var fn = child.frame.name;
            return fn === 'sliderthumb.png' || fn === 'sliderthumbsel.png';
        }
        return false;
    }

    function hookThumb(thumb) {
        if (thumb._iosHooked) return;
        thumb._iosHooked = true;
        thumb._iosOrigScale = thumb.scaleX || 0.7;

        var origSet = thumb.setTexture.bind(thumb);
        thumb._iosOrigSet = thumb.setTexture;

        thumb.setTexture = function(key, frame) {
            origSet(key, frame);
            if (this.texture && this.texture.key === 'GJ_WebSheet') {
                var fn = this.frame.name;
                if (fn === 'sliderthumb.png' && texKeyNormal) {
                    origSet(texKeyNormal);
                } else if (fn === 'sliderthumbsel.png' && texKeySelected) {
                    origSet(texKeySelected);
                }
            }
        };

        if (animEnabled) {
            setAnimOnThumb(thumb, true);
        }

        if (thumb.texture && thumb.texture.key === 'GJ_WebSheet') {
            var fn = thumb.frame.name;
            if (fn === 'sliderthumb.png' && texKeyNormal) {
                origSet(texKeyNormal);
            } else if (fn === 'sliderthumbsel.png' && texKeySelected) {
                origSet(texKeySelected);
            }
        }
    }

    function collectChildren(obj) {
        var items = [];
        if (!obj || !obj.list) return items;
        for (var i = 0; i < obj.list.length; i++) {
            var child = obj.list[i];
            items.push(child);
            if (child.list) items = items.concat(collectChildren(child));
        }
        return items;
    }

    function applyToAll() {
        forEachScene(function(scene) {
            var all = collectChildren(scene);
            for (var i = 0; i < all.length; i++) {
                if (isSliderThumb(all[i])) {
                    hookThumb(all[i]);
                }
            }
        });
    }

    function restoreThumb(thumb) {
        if (!thumb._iosHooked) return;
        thumb._iosHooked = false;

        if (thumb._iosOrigSet) {
            thumb.setTexture = thumb._iosOrigSet;
        }
        delete thumb._iosOrigSet;

        if (thumb._iosOnDrag) {
            thumb.off('drag', thumb._iosOnDrag);
            delete thumb._iosOnDrag;
        }
        if (thumb._iosOnDragEnd) {
            thumb.off('dragend', thumb._iosOnDragEnd);
            delete thumb._iosOnDragEnd;
        }

        var origScale = thumb._iosOrigScale || 0.7;
        thumb.setTexture('GJ_WebSheet', 'sliderthumb.png');
        thumb.setScale(origScale);
    }

    function restoreAll() {
        forEachScene(function(scene) {
            var all = collectChildren(scene);
            for (var i = 0; i < all.length; i++) {
                if (all[i]._iosHooked) {
                    restoreThumb(all[i]);
                }
            }
        });
    }

    function tick() {
        if (!texKeyNormal) {
            ensureIconTextures();
        } else {
            applyToAll();
        }
    }

    function setAnimOnThumb(thumb, enable) {
        if (enable) {
            thumb._iosOnDrag = function() { thumb.setScale(1.15); };
            thumb.on('drag', thumb._iosOnDrag);
            thumb._iosOnDragEnd = function() { thumb.setScale(1); };
            thumb.on('dragend', thumb._iosOnDragEnd);
        } else {
            if (thumb._iosOnDrag) { thumb.off('drag', thumb._iosOnDrag); delete thumb._iosOnDrag; }
            if (thumb._iosOnDragEnd) { thumb.off('dragend', thumb._iosOnDragEnd); delete thumb._iosOnDragEnd; }
        }
    }

    function iosOnSettings(modId, settings) {
        if (modId === 'IconOnSliders') {
            if (settings.animEnabled !== undefined && settings.animEnabled !== animEnabled) {
                animEnabled = settings.animEnabled;
                forEachScene(function(scene) {
                    var all = collectChildren(scene);
                    for (var i = 0; i < all.length; i++) {
                        if (all[i]._iosHooked) {
                            setAnimOnThumb(all[i], animEnabled);
                        }
                    }
                });
            }
        }
        if (modId === 'MoreIcons') {
            texKeyNormal = null;
            texKeySelected = null;
            loadingTexture = false;
            ensureIconTextures();
        }
    }
    window.__modApplySettings = iosOnSettings;
    if (!window.__modOnSettings) window.__modOnSettings = [];
    window.__modOnSettings.push(iosOnSettings);

    try {
        var saved = JSON.parse(localStorage.getItem('mod-settings-IconOnSliders') || '{}');
        animEnabled = saved.animEnabled !== false;
    } catch(e) {
        animEnabled = true;
    }

    tick();
    pollTimer = setInterval(tick, 500);

    window.__modCleanup = function() {
        if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
        restoreAll();
        texKeyNormal = null;
        texKeySelected = null;
    };
})();
