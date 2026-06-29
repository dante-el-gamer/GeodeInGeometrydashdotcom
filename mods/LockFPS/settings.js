const modSettings = [
    {
        key: 'defaultFps',
        label: 'Default FPS',
        type: 'range',
        default: 60,
        min: 10,
        max: 240,
        step: 1,
        hint: 'FPS limit when the mod is activated.'
    },
    {
        key: 'minFps',
        label: 'Minimum FPS (slider)',
        type: 'range',
        default: 10,
        min: 5,
        max: 60,
        step: 1,
        hint: 'Lowest value the in-game slider can reach.'
    },
    {
        key: 'maxFps',
        label: 'Maximum FPS (slider)',
        type: 'range',
        default: 240,
        min: 60,
        max: 999,
        step: 1,
        hint: 'Highest value the in-game slider can reach.'
    },
    {
        key: 'showOnStart',
        label: 'Show slider on start',
        type: 'toggle',
        default: true,
        hint: 'Show the FPS slider when the mod is enabled.'
    }
];
