(function() {
    if (typeof __fpsLimit === 'undefined') return;

    var targetFps = 60;
    var slider = null;
    var escBound = null;
    var isOn = false;
    var minFps = 10, maxFps = 240;

    function readSettings() {
        if (typeof modSettingsValues !== 'undefined' && modSettingsValues.LockFPS) {
            var s = modSettingsValues.LockFPS;
            targetFps = s.defaultFps || 60;
            minFps = s.minFps || 10;
            maxFps = s.maxFps || 240;
        }
    }

    function rebuildSlider() {
        if (slider && slider.parentNode) slider.parentNode.removeChild(slider);
        slider = buildSlider();
        document.body.appendChild(slider);
        var show = (typeof modSettingsValues !== 'undefined' && modSettingsValues.LockFPS)
            ? modSettingsValues.LockFPS.showOnStart !== false
            : true;
        slider.style.display = show ? 'flex' : 'none';
        if (isOn) {
            __fpsLimit.setTarget(targetFps);
        }
    }

    function applyNewSettings() {
        readSettings();
        rebuildSlider();
    }

    function buildSlider() {
        var el = document.createElement('div');
        el.innerHTML =
            '<div style="display:flex;align-items:center;gap:12px">' +
                '<span style="color:#aaa;font-size:12px;font-weight:600;letter-spacing:0.5px">FPS</span>' +
                '<input type="range" min="' + minFps + '" max="' + maxFps + '" value="' + targetFps + '" style="width:140px;accent-color:#0f0;cursor:pointer">' +
                '<span style="color:#0f0;font-size:14px;font-weight:700;min-width:44px;text-align:right;font-variant-numeric:tabular-nums">' + targetFps + '</span>' +
            '</div>';
        el.style.cssText = [
            'position:fixed', 'bottom:24px', 'left:50%', 'transform:translateX(-50%)',
            'z-index:9999', 'display:none', 'align-items:center',
            'background:rgba(0,0,0,0.82)', 'padding:10px 20px', 'border-radius:8px',
            'border:1px solid rgba(255,255,255,0.08)', 'backdrop-filter:blur(4px)',
            'font-family:sans-serif', 'user-select:none',
        ].join(';');

        var input = el.querySelector('input');
        var valSpan = el.querySelector('span');

        input.addEventListener('input', function() {
            targetFps = Number(input.value);
            valSpan.textContent = targetFps;
            if (isOn) __fpsLimit.setTarget(targetFps);
        });

        return el;
    }

    function toggle() {
        isOn = !isOn;
        if (isOn) {
            __fpsLimit.setTarget(targetFps);
            __fpsLimit.enable();
        } else {
            __fpsLimit.disable();
        }
        if (slider) {
            var input = slider.querySelector('input');
            var valSpan = slider.querySelector('span');
            input.value = targetFps;
            valSpan.textContent = targetFps;
        }
    }

    escBound = function(e) {
        if (e.key === 'Escape') {
            if (!slider) return;
            var hidden = slider.style.display === 'none';
            slider.style.display = hidden ? 'flex' : 'none';
        }
    };
    document.addEventListener('keydown', escBound);

    readSettings();
    slider = buildSlider();
    document.body.appendChild(slider);
    toggle();
    var show = (typeof modSettingsValues !== 'undefined' && modSettingsValues.LockFPS)
        ? modSettingsValues.LockFPS.showOnStart !== false
        : true;
    slider.style.display = show ? 'flex' : 'none';

    window.__modCleanup = function() {
        __fpsLimit.disable();
        document.removeEventListener('keydown', escBound);
        if (slider && slider.parentNode) slider.parentNode.removeChild(slider);
        slider = null;
    };

    window.__modApplySettings = function(modId, settings) {
        if (modId === 'LockFPS') {
            targetFps = settings.defaultFps || 60;
            minFps = settings.minFps || 10;
            maxFps = settings.maxFps || 240;
            rebuildSlider();
        }
    };
})();
