// Estructura para registrar los clics de forma independiente a los FPS
class InputManager {
    constructor() {
        this.inputs = [];
        this.setupListeners();
    }

    setupListeners() {
        // Escucha el evento de presión del botón de forma global
        window.addEventListener('mousedown', (event) => {
            if (event.button === 0) { // Click izquierdo
                this.registrarInput('press');
            }
        });

        // Escucha cuando se suelta el botón
        window.addEventListener('mouseup', (event) => {
            if (event.button === 0) {
                this.registrarInput('release');
            }
        });
    }

    registrarInput(action) {
        // performance.now() mide el tiempo en milisegundos con alta precisión
        const timestamp = performance.now(); 
        
        // Registramos el tipo de acción y el momento exacto
        this.inputs.push({
            action: action,
            time: timestamp
        });
    }

    // Método que el motor del juego/web puede llamar en cada ciclo (tick)
    procesarInputs(tiempoActual) {
        // Filtra y procesa los clics que ocurrieron hasta el momento actual del ciclo
        const inputsPorProcesar = this.inputs.filter(input => input.time <= tiempoActual);
        
        // Aquí ejecutas la lógica de tu juego/web (ej. saltar, disparar)
        inputsPorProcesar.forEach(input => {
            if (input.action === 'press') {
                console.log(`Acción 'press' ejecutada en milisegundo: ${input.time}`);
                // Lógica de presionar salto/acción
            } else if (input.action === 'release') {
                console.log(`Acción 'release' ejecutada en milisegundo: ${input.time}`);
                // Lógica de soltar
            }
        });

        // Limpiamos los inputs que ya fueron procesados
        this.inputs = this.inputs.filter(input => input.time > tiempoActual);
    }
}

// Inicializar el manejador
const inputManager = new InputManager();

// Ejemplo de bucle de físicas independiente de los fotogramas visuales
let lastTime = 0;
function gameLoop(timestamp) {
    // Calculamos el delta time entre frames
    let deltaTime = timestamp - lastTime;
    lastTime = timestamp;

    // Procesamos todos los clics que ocurrieron durante este lapso
    inputManager.procesarInputs(timestamp);

    // Siguiente frame
    requestAnimationFrame(gameLoop);
}

requestAnimationFrame(gameLoop);
