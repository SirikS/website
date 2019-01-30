var script = document.createElement('script');

// Import Jquery
script.src = '//code.jquery.com/jquery-1.11.0.min.js';
document.getElementsByTagName('head')[0].appendChild(script);

// Open the navbar automatically, makes sure you don't have to click twice when it first loads to close it.
function openpage()
{
    document.getElementById("mySidenav").style.width = "0";
}

// Function to open and close the navbar
function openNav() {
    // Check how wide the navbar is.
    var e = document.getElementById("mySidenav");
    // if the navbar is 250px wide, close it
    if (e.style.width == '250px')
    {
        document.getElementById("mySidenav").style.width = "0";
    }
    // Otherwise, open the navbar
    else
    {
        document.getElementById("mySidenav").style.width = "250px";
    }
}

// Function to load pictures in tabs on the profile page
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

// Function to change the text in the follow button from 'Adopt' to 'Abandon'.
function volgknop() {
    var x = document.getElementById("knop");
    if (x.innerHTML === "Abandon") {
        x.innerHTML = "Adopt";
    }
    else {
        x.innerHTML = "Abandon";
    }
}