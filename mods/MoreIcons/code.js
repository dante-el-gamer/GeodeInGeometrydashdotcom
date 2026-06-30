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

    // ── Main Menu Button (Phaser, left of Play) ───────────────────
    var menuBtnImage = null;
    var menuBtnCreated = false;
    var menuBtnFloatTween = null;
    var lastMenuActive = null;

    function getMainMenuScene() {
        var game = window.__phaserGame;
        if (!game || !game.scene) return null;
        var scenes = game.scene.scenes;
        for (var i = 0; i < scenes.length; i++) {
            if (scenes[i]._menuActive !== undefined) return scenes[i];
        }
        return null;
    }

    function addBouncyInteraction(btn, scene) {
        btn.on('pointerover', function() {
            if (scene.tweens) scene.tweens.add({ targets: btn, scaleX: btn._miBaseScale * 1.1, scaleY: btn._miBaseScale * 1.1, duration: 80, ease: 'Quad.Out' });
        });
        btn.on('pointerout', function() {
            if (scene.tweens) scene.tweens.add({ targets: btn, scaleX: btn._miBaseScale, scaleY: btn._miBaseScale, duration: 80, ease: 'Quad.Out' });
        });
        btn.on('pointerdown', function() {
            if (scene.tweens) scene.tweens.add({ targets: btn, scaleX: btn._miBaseScale * 0.9, scaleY: btn._miBaseScale * 0.9, duration: 40, ease: 'Quad.In' });
        });
        btn.on('pointerup', function() {
            if (scene.tweens) scene.tweens.add({ targets: btn, scaleX: btn._miBaseScale * 1.1, scaleY: btn._miBaseScale * 1.1, duration: 60, ease: 'Quad.Out' });
        });
    }

    function createMainMenuBtn(scene) {
        if (menuBtnCreated) return;
        var gameW = scene.sys.game.config.width;

        // Pre-load skin textures for when menu opens
        loadAllSkinTex(scene);

        var img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = function() {
            var texMan = scene.sys.textures;
            var texKey = 'mi_main_menu_btn';
            if (!texMan.exists(texKey)) texMan.addImage(texKey, img);

            var btnX = gameW / 2 - 200;
            var btnY = 320;
            menuBtnImage = scene.add.image(btnX, btnY, texKey);
            menuBtnImage.setScrollFactor(0);
            menuBtnImage.setDepth(30);
            menuBtnImage.setInteractive({ useHandCursor: true });
            var scale = 0.34;
            menuBtnImage.setScale(scale);
            menuBtnImage._miBaseScale = scale;
            menuBtnImage.setOrigin(0.5);

            addBouncyInteraction(menuBtnImage, scene);
            menuBtnImage.on('pointerup', function() { openSkinMenu(); });

            // Float animation (same as Play button: y 320↔324, 750ms Quad.InOut)
            if (scene.tweens) {
                menuBtnFloatTween = scene.tweens.add({
                    targets: menuBtnImage,
                    y: 326,
                    duration: 750,
                    ease: 'Quad.InOut',
                    yoyo: true,
                    repeat: -1
                });
            }

            menuBtnCreated = true;
        };
        img.src = 'mods/MoreIcons/assets/MainMenu/MainMenuButton.png';
    }

    function removeMainMenuBtn() {
        if (menuBtnImage) {
            if (menuBtnFloatTween) { menuBtnFloatTween.stop(); menuBtnFloatTween = null; }
            menuBtnImage.destroy();
            menuBtnImage = null;
        }
        menuBtnCreated = false;
    }

    // ── Icon Selection Overlay (Phaser Skin Menu) ────────────────
    var skinContainer = null;
    var skinIconPage = 1;
    var skinType = 'cube'; // 'cube','ship','ball','ufo','wave','robot','spider','swing'
    var skinLoadedTextures = {};
    var skinTypeButtons = [];
    var skinGridImages = [];
    var skinPageText = null;
    var skinLoadingSprite = null;
    var SKIN_DIR = 'mods/MoreIcons/assets/SkinMenu/';
    var ICON_TYPES = ['cube','ship','ball','ufo','wave','robot','spider','swing'];

    function loadSkinTex(key, file, scene) {
        if (skinLoadedTextures[key] || scene.sys.textures.exists(key)) { skinLoadedTextures[key] = true; return; }
        skinLoadedTextures[key] = false;
        var img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = function() {
            if (!scene.sys.textures.exists(key)) scene.sys.textures.addImage(key, img);
            skinLoadedTextures[key] = true;
        };
        img.src = SKIN_DIR + file;
    }

    function loadAllSkinTex(scene) {
        var texs = [
            ['mi_sk_tl', 'TopLeftEdge.png'], ['mi_sk_tr', 'TopRightEdge.png'],
            ['mi_sk_bl', 'ButtomLeftEdge.png'], ['mi_sk_br', 'BottomRightEdge.png'],
            ['mi_sk_cube','CubeButton.png'],['mi_sk_ship','ShipButton.png'],
            ['mi_sk_ball','BallButton.png'],['mi_sk_ufo','UfoButton.png'],
            ['mi_sk_wave','WaveButton.png'],['mi_sk_robot','RobotButton.png'],
            ['mi_sk_spider','SpiderButton.png'],['mi_sk_sc','SCButton.png'],
            ['mi_sk_izone','IconZone.png'],['mi_sk_lkey','LeftKeyButton.png'],
            ['mi_sk_rkey','RightKeyButton.png'],['mi_sk_color','ColorButton.png'],
            ['mi_sk_load','LoadingCircle.png']
        ];
        for (var i = 0; i < texs.length; i++) loadSkinTex(texs[i][0], texs[i][1], scene);
    }

    function createBgGradient(scene, w, h) {
        var key = 'mi_sk_bg';
        if (scene.sys.textures.exists(key)) return key;
        var c = document.createElement('canvas');
        c.width = Math.max(w, 1);
        c.height = Math.max(h, 1);
        var ctx = c.getContext('2d');
        var grad = ctx.createLinearGradient(0, 0, 0, h);
        grad.addColorStop(0, '#949494');
        grad.addColorStop(1, '#444444');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, c.width, c.height);
        scene.sys.textures.addCanvas(key, c);
        return key;
    }

    function openSkinMenu() {
        var scene = getMainMenuScene();
        if (!scene || skinContainer) return;

        var gameW = scene.sys.game.config.width;
        var gameH = scene.sys.game.config.height;

        skinContainer = scene.add.container(0, 0).setDepth(100).setScrollFactor(0);

        // Background gradient (sync)
        var bgKey = createBgGradient(scene, gameW, gameH);
        skinContainer.add(scene.add.image(gameW / 2, gameH / 2, bgKey).setDisplaySize(gameW, gameH));

        // Check if skin textures are loaded; if not, build when ready
        var allLoaded = true;
        var texKeys = ['mi_sk_tl','mi_sk_tr','mi_sk_bl','mi_sk_br','mi_sk_cube','mi_sk_ship',
            'mi_sk_ball','mi_sk_ufo','mi_sk_wave','mi_sk_robot','mi_sk_spider','mi_sk_sc',
            'mi_sk_izone','mi_sk_lkey','mi_sk_rkey','mi_sk_color','mi_sk_load'];
        for (var i = 0; i < texKeys.length; i++) {
            if (!scene.sys.textures.exists(texKeys[i])) { allLoaded = false; break; }
        }

        if (allLoaded) {
            buildSkinUI(scene, gameW, gameH);
        } else {
            // Load textures, then build
            loadAllSkinTex(scene);
            var retryInterval = setInterval(function() {
                var ready = true;
                for (var i = 0; i < texKeys.length; i++) {
                    if (!scene.sys.textures.exists(texKeys[i])) { ready = false; break; }
                }
                if (ready) {
                    clearInterval(retryInterval);
                    if (skinContainer && scene.sys.textures.exists(texKeys[0])) {
                        buildSkinUI(scene, gameW, gameH);
                    }
                }
            }, 100);
        }
    }

    function buildSkinUI(scene, gameW, gameH) {
        if (!skinContainer) return;

        // Corner edges - scaled to fit
        var eScale = Math.min(gameW, gameH) / 942 * 0.15;
        var eW = 942 * eScale;
        var eH = 942 * eScale;
        var tl = scene.add.image(0, 0, 'mi_sk_tl').setOrigin(0, 0).setDisplaySize(eW, eH);
        skinContainer.add(tl);
        var tr = scene.add.image(gameW, 0, 'mi_sk_tr').setOrigin(1, 0).setDisplaySize(eW, eH);
        skinContainer.add(tr);
        var bl = scene.add.image(0, gameH, 'mi_sk_bl').setOrigin(0, 1).setDisplaySize(eW, eH);
        skinContainer.add(bl);
        var br = scene.add.image(gameW, gameH, 'mi_sk_br').setOrigin(1, 1).setDisplaySize(eW, eH);
        skinContainer.add(br);

        // Close button (✕ text in top-right)
        var closeBtn = scene.add.text(gameW - 10, 10, '✕', {
            fontFamily: 'sans-serif', fontSize: '32px', color: 'rgba(255,255,255,0.7)'
        }).setOrigin(1, 0).setStroke('#000', 4).setInteractive({ useHandCursor: true });
        closeBtn.on('pointerdown', closeSkinMenu);
        skinContainer.add(closeBtn);

        // Type buttons row - centered
        var btnScale = Math.min(1, (gameW - 100) / (ICON_TYPES.length * 157));
        var btnW = 157 * btnScale;
        var totalBtnW = ICON_TYPES.length * btnW;
        var startX = (gameW - totalBtnW) / 2 + btnW / 2;
        var btnY = 30 + btnW * 0.5;

        for (var i = 0; i < ICON_TYPES.length; i++) {
            (function(idx, type) {
                var texKey = 'mi_sk_' + type;
                var btn = scene.add.image(startX + idx * btnW, btnY, texKey).setDisplaySize(btnW, btnW * 154 / 157).setInteractive({ useHandCursor: true }).setAlpha(0.5);
                btn._miType = type;
                btn.on('pointerdown', function() {
                    skinType = this._miType;
                    updateTypeButtons();
                    skinIconPage = 1;
                    renderSkinGrid(scene, gameW, gameH);
                });
                skinContainer.add(btn);
                skinTypeButtons.push(btn);
            })(i, ICON_TYPES[i]);
        }
        updateTypeButtons();

        // Icon zone
        var izScale = Math.min(1, (gameW - 120) / 543);
        var izW = 543 * izScale;
        var izH = 173 * izScale;
        var izY = btnY + btnW * 0.6 + izH / 2 + 10;
        var izX = gameW / 2;
        var iz = scene.add.image(izX, izY, 'mi_sk_izone').setDisplaySize(izW, izH);
        skinContainer.add(iz);

        // Arrow buttons
        var arrowScale = Math.min(1, izScale * 0.8);
        var arrowW = 61 * arrowScale;
        var arrowH = 74 * arrowScale;
        var arrowY = izY;

        var lk = scene.add.image(izX - izW / 2 - arrowW / 2 - 5, arrowY, 'mi_sk_lkey').setDisplaySize(arrowW, arrowH).setInteractive({ useHandCursor: true });
        lk.on('pointerdown', function() { if (skinIconPage > 1) { skinIconPage--; renderSkinGrid(scene, gameW, gameH); } });
        skinContainer.add(lk);

        var rk = scene.add.image(izX + izW / 2 + arrowW / 2 + 5, arrowY, 'mi_sk_rkey').setDisplaySize(arrowW, arrowH).setInteractive({ useHandCursor: true });
        rk.on('pointerdown', function() { var t = getTotalPages(); if (skinIconPage < t) { skinIconPage++; renderSkinGrid(scene, gameW, gameH); } });
        skinContainer.add(rk);

        // Page text
        skinPageText = scene.add.text(izX, izY + izH / 2 + 20, '', {
            fontFamily: 'Pusab', fontSize: '18px', color: '#fff'
        }).setOrigin(0.5).setStroke('#000', 3);
        skinContainer.add(skinPageText);

        // Color button
        var cbScale = Math.min(1, (gameW * 0.15) / 156);
        var cbW = 156 * cbScale;
        var cbH = 140 * cbScale;
        var cb = scene.add.image(cbW / 2 + 20, gameH - cbH / 2 - 20, 'mi_sk_color').setDisplaySize(cbW, cbH).setInteractive({ useHandCursor: true });
        skinContainer.add(cb);

        // Loading circle (hidden)
        var lcSize = Math.min(gameW, gameH) * 0.15;
        skinLoadingSprite = scene.add.image(gameW / 2, gameH / 2, 'mi_sk_load').setDisplaySize(lcSize, lcSize).setVisible(false).setDepth(101);
        skinContainer.add(skinLoadingSprite);

        renderSkinGrid(scene, gameW, gameH);
    }

    function getTotalPages() {
        return Math.ceil(485 / 50);
    }

    function updateTypeButtons() {
        for (var i = 0; i < skinTypeButtons.length; i++) {
            var b = skinTypeButtons[i];
            b.setAlpha(b._miType === skinType ? 1 : 0.5);
        }
    }

    function renderSkinGrid(scene, gameW, gameH) {
        for (var i = 0; i < skinGridImages.length; i++) skinGridImages[i].destroy();
        skinGridImages = [];

        var izScale = Math.min(1, (gameW - 120) / 543);
        var izW = 543 * izScale;
        var izH = 173 * izScale;
        var btnScale = Math.min(1, (gameW - 100) / (ICON_TYPES.length * 157));
        var btnW = 157 * btnScale;
        var izY = 30 + btnW * 0.6 + izH / 2 + 10 + btnW * 0.5;
        var izX = gameW / 2;

        var cols = 12;
        var rows = 3;
        var padX = 12;
        var padY = 12;
        var cellW = (izW - padX * 2) / cols;
        var cellH = (izH - padY * 2) / rows;
        var iconSize = Math.min(cellW, cellH) * 0.75;
        var gridStartX = izX - izW / 2 + padX + cellW / 2;
        var gridStartY = izY - izH / 2 + padY + cellH / 2;

        var perPage = cols * rows;
        var start = (skinIconPage - 1) * perPage + 1;
        var end = Math.min(start + perPage - 1, 485);

        for (var i = start; i <= end; i++) {
            (function(num) {
                var idx = (num - start);
                var col = idx % cols;
                var row = Math.floor(idx / cols);
                var x = gridStartX + col * cellW;
                var y = gridStartY + row * cellH;
                var img = new Image();
                img.crossOrigin = 'anonymous';
                img.onload = function() {
                    var texKey = 'mi_sk_icon_' + num;
                    if (!scene.sys.textures.exists(texKey)) scene.sys.textures.addImage(texKey, img);
                    var icon = scene.add.image(x, y, texKey).setDisplaySize(iconSize, iconSize).setInteractive({ useHandCursor: true });
                    icon.on('pointerdown', function() { selectSkinIcon(num); });
                    skinContainer.add(icon);
                    skinGridImages.push(icon);
                };
                img.src = 'Icons/cube/cube_' + num + '.png';
            })(i);
        }

        var tp = getTotalPages(perPage);
        var curPage = skinIconPage;
        skinPageText.setText('Page ' + curPage + ' / ' + tp);
    }

    function getTotalPages(perPage) {
        return Math.ceil(485 / (perPage || 36));
    }

    function selectSkinIcon(num) {
        currentIcon = num;
        var settings = JSON.parse(localStorage.getItem('mod-settings-MoreIcons') || '{}');
        settings.cubeIcon = num;
        localStorage.setItem('mod-settings-MoreIcons', JSON.stringify(settings));
        var scene = getScene();
        if (scene && scene._player) applyIcon(scene, scene._player, currentIcon, currentColor1, currentColor2, currentGlow, currentCustomUrl);
        // Don't close menu - user must close manually
    }

    function closeSkinMenu() {
        if (skinContainer) { skinContainer.destroy(); skinContainer = null; }
        skinGridImages = [];
        skinTypeButtons = [];
        skinPageText = null;
        skinLoadingSprite = null;
    }

    menuBtnCreated = false;
    lastMenuActive = null;

    var origTick = tick;
    tick = function() {
        origTick();
        var scene = getMainMenuScene();
        if (!scene) return;
        var isMenuActive = scene._menuActive;
        if (isMenuActive !== lastMenuActive) {
            lastMenuActive = isMenuActive;
            if (isMenuActive) {
                createMainMenuBtn(scene);
            } else {
                removeMainMenuBtn();
                closeSkinMenu();
            }
        }
    };

    tick();
    pollTimer = setInterval(tick, 300);

    window.__moreIcons = {
        recolorIcon: recolorIcon,
        getSettings: function() { return { icon: currentIcon, color1: currentColor1, color2: currentColor2, glow: currentGlow, customUrl: currentCustomUrl }; }
    };

    window.__modCleanup = function() {
        closeSkinMenu();
        removeMainMenuBtn();
        if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
        currentIcon = null;
        lastPlayer = null;
        var scene = getScene();
        if (scene && scene._player) restoreIcon(scene, scene._player);
    };
})();
