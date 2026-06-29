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
        count: 129,
        hint: 'Select your cube icon (1-129 available).'
    },
    {
        key: 'color1',
        label: 'Color 1 (light)',
        type: 'color',
        default: DEFAULT_COLOR_1,
        hint: 'Replaces the light areas of the icon.'
    },
    {
        key: 'color2',
        label: 'Color 2 (dark)',
        type: 'color',
        default: DEFAULT_COLOR_2,
        hint: 'Replaces the dark areas (black outlines stay).'
    }
];
