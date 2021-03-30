if (passedID == "None"){
    var id = readCookie("idnumber");
}
else{
    var id = passedID;
}

if (id == null){
    id = prompt("Skriv in ditt ID:");
    a_or_id = "?id=";
}

function htmlEncode(value) { 
    return $('<div/>').text(value).html(); 
}
var url = requestURL + a_or_id + id;


if (privateID){
    $("#maintext").text(prompt("Skriv in namn på schemat:"));
}
else{
    $('#maintext').text(id);
}

$('#subtext').text(url);

//var witdh = $('#qr-code').width();
//var height = $('#qr-code').height()

let finalURL = 'https://chart.googleapis.com/chart?cht=qr&chl=' + htmlEncode(url) + '&chs=160x160&chld=L|0' 

$('#qr-code').attr('src', finalURL);

//window.setTimeout(document.querySelector('img').complete, 100); // Wait for image to load
//window.print();