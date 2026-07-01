// =============================================================================
//  Skin Menu — Main menu button + icon selection overlay
//  Cargado desde code.js via codeFiles.
//  Usa window.__moreIcons para acceder al motor de iconos.
// =============================================================================
(function() {
    var mi = window.__moreIcons;

    // ── Shared state ─────────────────────────────────────────────
    var menuBtnImage = null;
    var menuBtnCreated = false;
    var menuBtnFloatTween = null;
    var lastMenuActive = null;

    var skinContainer = null;
    var skinIconPage = 1;
    var skinType = 'cube';
    var skinLoadedTextures = {};
    var skinTypeButtons = [];
    var skinGridImages = [];
    var skinPageText = null;
    var skinLoadingSprite = null;
    var SKIN_DIR = 'mods/MoreIcons/assets/SkinMenu/';
    var ICON_TYPES = ['cube','ship','ball','ufo','wave','robot','spider','swing'];
    var TYPE_TEX = { cube:'mi_sk_cube', ship:'mi_sk_ship', ball:'mi_sk_ball', ufo:'mi_sk_ufo',
        wave:'mi_sk_wave', robot:'mi_sk_robot', spider:'mi_sk_spider', swing:'mi_sk_sc' };

    // ── Texture loading ──────────────────────────────────────────
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

    // ── Main menu button ─────────────────────────────────────────
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

    // ── Background gradient ──────────────────────────────────────
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

    // ── Skin menu open / build ───────────────────────────────────
    function openSkinMenu() {
        var scene = mi.getMainMenuScene();
        if (!scene || skinContainer) return;

        var gameW = scene.sys.game.config.width;
        var gameH = scene.sys.game.config.height;

        skinContainer = scene.add.container(0, 0).setDepth(100).setScrollFactor(0);

        // Block input to elements behind the skin menu
        var blocker = scene.add.rectangle(gameW / 2, gameH / 2, gameW, gameH, 0x000000, 0)
            .setInteractive()
            .setDepth(200)
            .setScrollFactor(0);
        skinContainer.add(blocker);

        var bgKey = createBgGradient(scene, gameW, gameH);
        skinContainer.add(scene.add.image(gameW / 2, gameH / 2, bgKey).setDisplaySize(gameW, gameH));

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

        // Corner edges
        var eScale = Math.min(gameW, gameH) / 942 * 0.15;
        var eW = 942 * eScale;
        var eH = 942 * eScale;
        skinContainer.add(scene.add.image(0, 0, 'mi_sk_tl').setOrigin(0, 0).setDisplaySize(eW, eH));
        skinContainer.add(scene.add.image(gameW, 0, 'mi_sk_tr').setOrigin(1, 0).setDisplaySize(eW, eH));
        skinContainer.add(scene.add.image(0, gameH, 'mi_sk_bl').setOrigin(0, 1).setDisplaySize(eW, eH));
        skinContainer.add(scene.add.image(gameW, gameH, 'mi_sk_br').setOrigin(1, 1).setDisplaySize(eW, eH));

        // Close button
        var closeBtn = scene.add.text(gameW - 10, 10, '\u2715', {
            fontFamily: 'sans-serif', fontSize: '32px', color: 'rgba(255,255,255,0.7)'
        }).setOrigin(1, 0).setStroke('#000', 4).setInteractive({ useHandCursor: true });
        closeBtn.on('pointerdown', closeSkinMenu);
        skinContainer.add(closeBtn);

        // Type buttons row - bottom
        var btnW = 24;
        var btnH = 23;
        var totalBtnW = ICON_TYPES.length * (btnW + 4);
        var startX = (gameW - totalBtnW) / 2 + btnW / 2;
        var btnY = gameH - btnH * 0.5 - 20;

        for (var i = 0; i < ICON_TYPES.length; i++) {
            (function(idx, type) {
                var texKey = TYPE_TEX[type] || 'mi_sk_' + type;
                var btn = scene.add.image(startX + idx * (btnW + 4), btnY, texKey)
                    .setDisplaySize(btnW, btnH)
                    .setInteractive({ useHandCursor: true }).setAlpha(0.5);
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
        var izY = gameH * 0.36;
        var izX = gameW / 2;
        skinContainer.add(scene.add.image(izX, izY, 'mi_sk_izone').setDisplaySize(izW, izH));

        // Arrow buttons
        var arrowScale = Math.min(1, izScale * 0.8);
        var arrowW = 61 * arrowScale;
        var arrowH = 74 * arrowScale;
        var arrowY = izY;

        var lk = scene.add.image(izX - izW / 2 - arrowW / 2 - 5, arrowY, 'mi_sk_lkey')
            .setDisplaySize(arrowW, arrowH).setInteractive({ useHandCursor: true });
        lk.on('pointerdown', function() { if (skinIconPage > 1) { skinIconPage--; renderSkinGrid(scene, gameW, gameH); } });
        skinContainer.add(lk);

        var rk = scene.add.image(izX + izW / 2 + arrowW / 2 + 5, arrowY, 'mi_sk_rkey')
            .setDisplaySize(arrowW, arrowH).setInteractive({ useHandCursor: true });
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
        skinContainer.add(scene.add.image(cbW / 2 + 20, gameH - cbH / 2 - 20, 'mi_sk_color')
            .setDisplaySize(cbW, cbH).setInteractive({ useHandCursor: true }));

        // Loading circle (hidden)
        var lcSize = Math.min(gameW, gameH) * 0.15;
        skinLoadingSprite = scene.add.image(gameW / 2, gameH / 2, 'mi_sk_load')
            .setDisplaySize(lcSize, lcSize).setVisible(false).setDepth(101);
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
        var izY = gameH * 0.36;
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
        skinPageText.setText('Page ' + skinIconPage + ' / ' + tp);
    }

    function getTotalPages(perPage) {
        return Math.ceil(485 / (perPage || 36));
    }

    function selectSkinIcon(num) {
        mi.currentIcon = num;
        var settings = JSON.parse(localStorage.getItem('mod-settings-MoreIcons') || '{}');
        settings.cubeIcon = num;
        localStorage.setItem('mod-settings-MoreIcons', JSON.stringify(settings));
        var scene = mi.getScene();
        if (scene && scene._player) mi.applyIcon(scene, scene._player, mi.currentIcon, mi.currentColor1, mi.currentColor2, mi.currentGlow, mi.currentCustomUrl);
    }

    function closeSkinMenu() {
        if (skinContainer) {
            skinContainer.destroy();
            skinContainer = null;
        }
        skinGridImages = [];
        skinTypeButtons = [];
        skinPageText = null;
        skinLoadingSprite = null;
    }

    // ── Register tick hook ───────────────────────────────────────
    mi.onTick.push(function() {
        var scene = mi.getMainMenuScene();
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
    });

    // ── Register cleanup ─────────────────────────────────────────
    mi.cleanup = function() {
        closeSkinMenu();
        removeMainMenuBtn();
    };
})();
