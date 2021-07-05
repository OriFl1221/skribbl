const form = document.getElementById("chat-form");
const msgInput = document.getElementById("msg-chat-form");
const usernameInput = document.getElementById("username");
const chatbox = document.getElementById("msg-container");
const urlParams = new URLSearchParams(window.location.search);

// Create WebSocket connection.
let socket = new WebSocket("ws://172.19.130.83:443/" + urlParams.get("room"));

let mouseCords = {
    x: 0,
    y: 0
};
let pmouseCords = mouseCords;

fetch('/wsLocation').then(e => e.json()).then(e => {
    socket = new WebSocket(`ws://${e.ip}:${e.port}/` + urlParams.get("room"));

    // on connect inform server of new join
    socket.addEventListener("open", (event) => {
        console.log("connected");

        socket.send(
            JSON.stringify({
                type: "newJoin",
            })
        );

    });

    socket.addEventListener("close", (event) => {
        console.log("disconnected");
    });

    // </div><img src=x onerror=alert(1)//><div>
    // Listen for messages
    socket.addEventListener("message", (event) => {
        let msg = JSON.parse(event.data);
        console.log("Message from server ", msg);

        // execute code acording to msg from server
        if (msg.type == "chatMsg") {
            // add new chat msg
            chatbox.innerHTML += `<div class="card light-blue lighten-5">${DOMPurify.sanitize(
            escape(msg.username + ": " + msg.content)
        )}</div>`;
        } else if (msg.type == "newJoin") {
            // render previous msgs
            chatbox.innerHTML = "";
            for (let i = 0; i < msg.content.chat.length; i++) {
                chatbox.innerHTML += `<div class="card light-blue lighten-5">${DOMPurify.sanitize(
                escape(
                    msg.content.chat[i].username +
                        ": " +
                        msg.content.chat[i].content
                )
            )}</div>`;
            }

            // render canvas
            for (let i = 0; i < msg.content.canvas.length; i++) {
                if (msg.content.canvas[i].type == "mousePress") {
                    dataToCanvas(msg.content.canvas[i]);
                } else {
                    pmouseCords = mouseCords;
                }
            }
        } else if (msg.type == "mousePress") {
            // update canvas
            dataToCanvas(msg);
        } else if (msg.type == "mouseReleased") {
            pmouseCords = mouseCords;
        } else if (msg.type == "colorChange") {
            stroke(msg.color);
        }
    });

})


form.onsubmit = (e) => {
    e.preventDefault();
    if (msgInput.value)
        // if msg isnt empty send jsonobject
        socket.send(
            JSON.stringify({
                type: "chatMsg",
                username: usernameInput.value || "no username",
                content: msgInput.value,
            })
        );
};

function escape(string) {
    const map = {
        "<": "&lt;",
        "&": "&amp;",
        ">": "&gt;",
        "/": "&#x2F;",
        '"': "&quot;",
        "'": "&#x27;",
    };
    // using regex to replace dangerous characters with escaped versions
    const reg = /[&<>"'/]/gi;
    return string.replace(reg, (match) => map[match]);
}

function dataToCanvas(data) {
    mouseCords.x = data.x;
    mouseCords.y = data.y;
    line(mouseCords.x, mouseCords.y, pmouseCords.x, pmouseCords.y);
    pmouseCords = {
        x: mouseCords.x,
        y: mouseCords.y
    };
}

// displays the room id. important to escape string to prevent XSS like http://localhost:8080/room/index.html?room=</h5><img src=x onerror=alert(1)//><h5>
document.getElementById("room-code").innerHTML =
    "Room Code: " + DOMPurify.sanitize(escape(urlParams.get("room")));

document.getElementById("display-name").innerHTML =
    "Name: " + DOMPurify.sanitize(escape(urlParams.get("name")));