// get DOM elements
const canvasDiv = document.getElementById("canvas-container");
const colorIcons = document.getElementsByClassName("color");

const colorTable = {
    "white-text": "#ffffff",
    "black-text": "#000000",
    "green-text text-darken-4": "#1b5e20",
    "green-text": "#4caf50",
    "teal-text text-darken-3": "#00695c",
    "cyan-text": "#00bcd4",
    "blue-text text-darken-4": "#0d47a1",
    "blue-text": "#2196f3",
    "blue-text text-lighten-3": "#90caf9",
    "purple-text text-darken-4": "#4a148c",
    "pink-text": "#e91e63",
    "red-text text-darken-1": "#e53935",
    "red-text text-darken-4": "#b71c1c",
    "brown-text text-darken-2": "#5d4037",
    "orange-text text-darken-2": "#f57c00",
    "yellow-text text-accent-4": "#ffd600",
};

function setup() {
    // setup default view of the canvas and place it in correct div
    let canvas = createCanvas(800, 400);
    canvas.parent("canvas-container");
    background(255);
}

function draw() {
    // if user presses inside canvas
    if (
        mouseIsPressed &&
        mouseX > 0 &&
        mouseX < width &&
        mouseY > 0 &&
        mouseY < height
    ) {
        // draw where user pressed
        line(mouseX, mouseY, pmouseX, pmouseY);

        // send data to server
        socket.send(
            JSON.stringify({
                type: "mousePress",
                x: mouseX,
                y: mouseY,
            })
        );
    }
}

function mouseReleased() {
    // update server when user stops drawing
    if (mouseX > 0 && mouseX < width && mouseY > 0 && mouseY < height)
        socket.send(
            JSON.stringify({
                type: "mouseReleased",
            })
        );
}

// setup all color change buttons
for (let i = 0; i < colorIcons.length; i++) {
    colorIcons[i].onclick = () => {
        // gets color value
        let colorDescription = "";
        for (let j = 0; j < colorIcons[i].classList.length; j++)
            if (colorIcons[i].classList[j].includes("text"))
                colorDescription += colorIcons[i].classList[j] + " ";
        colorDescription = colorDescription.trim();

        // sets color value in canvas
        stroke(colorTable[colorDescription]);

        // sends color change to server
        socket.send(
            JSON.stringify({
                type: "colorChange",
                color: colorTable[colorDescription],
            })
        );
    };
}
