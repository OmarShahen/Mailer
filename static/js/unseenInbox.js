getUnseenMails();
setInterval(getUnseenMails, 5000);

function getUnseenMails()
{
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function()
    {
        if(this.status == 200 && this.readyState == 4)
        {
            let unseenMails = JSON.parse(this.responseText)["unseen_mails"];
            document.querySelector("#unseenMails").innerHTML = unseenMails;
        }
    };
    xhttp.open("GET", "{{url_for('user_mail_bp.unseen_inbox', user_mail = user_mail)}}", true);
    xhttp.send();
}