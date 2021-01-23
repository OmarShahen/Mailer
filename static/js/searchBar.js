
document.querySelector("#searchBar").addEventListener("keyup", () => {
    let searchBarValue = document.querySelector("#searchBar").value;
    let allMails = document.querySelectorAll("#userMail");
    for(let i=0;i<allMails.length;i++)
    {
        mail = allMails[i].innerHTML.toUpperCase()
        if(mail.indexOf(searchBarValue.toUpperCase()) > -1)
        {
            allMails[i].style.display = '';
        }else
        {
            allMails[i].style.display = "none";
        }
    }
});
