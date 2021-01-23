
setInterval(updateServer, 5000);
function updateServer()
{
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function()
    {
        if(this.readyState == 4 && this.status == 200)
        {
            console.log(JSON.parse(this.responseText));
        }
    };

    xhttp.open("GET", "{{url_for('user_profile_bp.user_activity')}}", true)
    xhttp.send();
}