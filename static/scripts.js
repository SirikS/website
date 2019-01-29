var script = document.createElement('script');

script.src = '//code.jquery.com/jquery-1.11.0.min.js';
document.getElementsByTagName('head')[0].appendChild(script);

// open de navbar automatisch, zorgt dat je niet de eerste keer 2x moet klikken om hem dicht te doen
function openpage()
{
    document.getElementById("mySidenav").style.width = "0";
}

//  functie op de navbar open en dicht te doen
function openNav() {
    // kijk hoe breed de navbar is
    var e = document.getElementById("mySidenav");
    // als de navbar 250px is, sluit hem dan
    if (e.style.width == '250px')
    {
        document.getElementById("mySidenav").style.width = "0";
    }
    // anders, open de navbar
    else
    {
        document.getElementById("mySidenav").style.width = "250px";
    }
}

function fotoladen(evt, soortfoto) {
    // Declare all variables
    var i, tabcontent, tablinks;
    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(soortfoto).style.display = "grid";
    evt.currentTarget.className += " active";
}
function volgknop() {
    var x = document.getElementById("knop");
    if (x.innerHTML === "Abandon") {
        x.innerHTML = "Adopt";
    }
    else {
        x.innerHTML = "Abandon";
    }
}