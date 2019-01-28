<script src="//ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>;

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

$(function() {
// button staat hier voor de button tag en het #knop staat voor het id van de button -->
    $('button#knop').bind('click', function() {
    $.getJSON('/follow/{{ userid }}',
    function(data) {
        //do nothing
            });
        return false;
    });
});

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
    document.getElementById(soortfoto).style.display = "flex";
    evt.currentTarget.className += " active";
}
function volgknop() {
    var x = document.getElementById("knop");
    if (x.innerHTML === "Ontvolg") {
        x.innerHTML = "Volg";
    }
    else {
        x.innerHTML = "Ontvolg";
    }
}

var apikey = 'CKjyWZfmOSGZIuHTwxgR5YB91CBmT7pj';
$(document).ready(function() {
  /*
  * The following two functions are used for making the API call using
  * pure Javascript. I wouldn't worry about the details
  */
  function encodeQueryData(data)
  {
     var ret = [];
     for (var d in data)
        ret.push(encodeURIComponent(d) + "=" + encodeURIComponent(data[d]));
     return ret.join("&");
  }
  function httpGetAsync(theUrl, callback)
  {
      var xmlHttp = new XMLHttpRequest();
      xmlHttp.onreadystatechange = function() {
          if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
              callback(xmlHttp.responseText);
      };
      xmlHttp.open("GET", theUrl, true); // true for asynchronous
      xmlHttp.send(null);
  }

  /*
  * The following functions are what do the work for retrieving and displaying gifs
  * that we search for.
  */
 function getGif(query) {
    console.log(query);
    query = query.replace(' ', '+');
    var params = { 'api_key': apikey, 'q': query};
    params = encodeQueryData(params);
    // api from https://github.com/Giphy/GiphyAPI#search-endpoint
    httpGetAsync('https://api.giphy.com/v1/gifs/search?' + params, function(data) {
      var gifs = JSON.parse(data);
      var firstgif = gifs.data[0].images.fixed_width.url;
      $("#image").html("<img src='" + firstgif + "'>");
      console.log(gifs.data);
    });
  }

function uploadGif(query) {
    console.log(query);
    query = query.replace(' ', '+');
    var params = { 'api_key': apikey, 'q': query};
    params = encodeQueryData(params);
    httpGetAsync('https://api.giphy.com/v1/gifs/search?' + params, function(data) {
      var gifs = JSON.parse(data);
      console.log(gifs.data[0].images.original_width.url);
      document.getElementById('gif').setAttribute('value', gifs.data[0].images.original.url);
    });
  }
  $("#submitButton").on("click", function() {
    var query = $("#inputQuery").val();
    getGif(query);
    uploadGif(query);
  });
});


$(document).ready(function() {
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function(e) {
                $('.img-preview').attr('src', e.target.result);
            };
            reader.readAsDataURL(input.files[0]);
        }
    }
    $("#logo-id").change(function() {
        readURL(this);
    });
});