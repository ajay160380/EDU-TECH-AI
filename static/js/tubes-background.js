/**
 * Tubes Interactive 3D Background Component
 * Wraps threejs-components TubesCursor effect to render neon tubes following the cursor in 3D space.
 */
class TubesBackground {
    constructor(canvas, options = {}) {
        this.canvas = typeof canvas === 'string' ? document.querySelector(canvas) : canvas;
        if (!this.canvas) return;

        this.options = Object.assign({
            colors: ["#f967fb", "#53bc28", "#6958d5"],
            lightsIntensity: 200,
            lightsColors: ["#83f36e", "#fe8a2e", "#ff008a", "#60aed5"],
            enableClickInteraction: true
        }, options);

        this.app = null;
        this.init();
    }

    async init() {
        try {
            // Dynamically import the TubesCursor build from the CDN
            const module = await import('https://cdn.jsdelivr.net/npm/threejs-components@0.0.19/build/cursors/tubes1.min.js');
            const TubesCursor = module.default;

            this.app = TubesCursor(this.canvas, {
                tubes: {
                    colors: this.options.colors,
                    lights: {
                        intensity: this.options.lightsIntensity,
                        colors: this.options.lightsColors
                    }
                }
            });

            if (this.options.enableClickInteraction) {
                this.clickHandler = () => this.randomize();
                // Attach click trigger to parent overlay container so it registers clicks easily
                const parent = this.canvas.parentElement;
                if (parent) {
                    parent.addEventListener('click', this.clickHandler);
                    parent.style.cursor = 'pointer';
                }
            }

        } catch (error) {
            console.error("Failed to load TubesCursor:", error);
        }
    }

    randomColors(count) {
        return new Array(count)
            .fill(0)
            .map(() => "#" + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0'));
    }

    randomize() {
        if (!this.app) return;
        const colors = this.randomColors(3);
        const lightsColors = this.randomColors(4);
        this.app.tubes.setColors(colors);
        this.app.tubes.setLightsColors(lightsColors);
    }

    destroy() {
        if (this.clickHandler) {
            const parent = this.canvas.parentElement;
            if (parent) {
                parent.removeEventListener('click', this.clickHandler);
            }
        }
        this.app = null;
    }
}
window.TubesBackground = TubesBackground;
