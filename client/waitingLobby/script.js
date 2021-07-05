const urlParams = new URLSearchParams(window.location.search);

document.getElementById("display-name").innerHTML =
    "Name: " + DOMPurify.sanitize(escape(urlParams.get("name")));