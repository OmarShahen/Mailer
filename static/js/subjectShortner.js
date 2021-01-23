document.querySelector("body").onload = adjustSubjects();
function adjustSubjects()
{
    let subjects = document.querySelectorAll("#mailSubject");
    for(let i=0;i<subjects.length;i++)
    {
        if(subjects[i].innerHTML.length > 44)
        {
            subjects[i].innerHTML = subjects[i].innerHTML.slice(0, 45) + "...";
        }
    }
}