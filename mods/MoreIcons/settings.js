var DEFAULT_COLOR_1 = '#ffffff';
var DEFAULT_COLOR_2 = '#000000';

const modSettings = [
    {
        key: 'cubeIcon',
        label: 'Cube icon',
        type: 'icon-grid',
        iconBase: 'Icons/cube/cube_',
        iconExt: '.png',
        default: 1,
        count: 485,
        hint: 'Select your cube icon (1-485 available).'
    },
    {
        key: 'color1',
        label: 'Color 1 (primary)',
        type: 'gd-color',
        default: DEFAULT_COLOR_1,
        hint: 'Replaces the light areas of the icon. Click a GD palette swatch or use hex.'
    },
    {
        key: 'color2',
        label: 'Color 2 (secondary)',
        type: 'gd-color',
        default: DEFAULT_COLOR_2,
        hint: 'Replaces the dark areas (black outlines stay). Click a GD palette swatch or use hex.'
    },
    {
        key: 'glow',
        label: 'Glow effect',
        type: 'toggle',
        default: false,
        hint: 'Adds a glow around the icon (uses Color 2 if enabled).'
    },
    {
        key: 'customIcon',
        label: 'Custom icon URL',
        type: 'image-url',
        default: '',
        hint: 'Enter a direct image URL (PNG/GIF) to use as your icon. Overrides the cube selection.'
    },
    {
        key: 'importProfile',
        label: 'Import from GD player',
        type: 'profile-import',
        placeholder: 'GD Username',
        default: '',
        hint: 'Fetch a real player\'s colors and glow from GDBrowser.',
        targets: { color1: 'color1', color2: 'color2', glow: 'glow', cubeIcon: 'cubeIcon' }
    }
];
