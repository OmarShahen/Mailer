let rowClass = "row justify-content-center text-white";
let userStatusDiv = document.querySelector("#userStatusDiv");
let userStatusMessage = document.querySelector("#userStatus");

if(!navigator.onLine)
{
    userStatusDiv.className = rowClass + " " + "bg-secondary";
        userStatusMessage.innerHTML = "connection lost";
        $("#userStatusDiv").fadeIn("fast");
}

window.addEventListener("online", () => {
    userStatusDiv.className = rowClass + " " + "bg-success";
    userStatusMessage.innerHTML = "connected";
    $("#userStatusDiv").fadeIn("fast");
    setTimeout(() => {$("#userStatusDiv").fadeOut()}, 1000);
    });
    window.addEventListener("offline", () => {
        userStatusDiv.className = rowClass + " " + "bg-secondary";
        userStatusMessage.innerHTML = "connection lost";
        $("#userStatusDiv").fadeIn("fast");
    });