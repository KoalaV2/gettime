function htmlEncode(value) { 
    return $('<div/>').text(value).html(); 
}

// Set ID
var id = passedID;
if (id == "None"){
    a_or_id = "?id=";
    var id = readCookie("idnumber");
    if (id == null){
        id = prompt("Skriv in ditt ID:"); 
    }
}

// Create gettime URL
var url = requestURL + a_or_id + id;

// Change text to print
$("#maintext").text(privateID ? prompt("Skriv in namn på schemat:") : id)
$('#subtext').text(url);

// Link to QR code
let finalURL = 'https://chart.googleapis.com/chart?cht=qr&chl=' + htmlEncode(url) + '&chs=160x160&chld=L|0' 
$('#qr-code').attr('src', finalURL);

//window.setTimeout(document.querySelector('img').complete, 100); // Wait for image to load
//window.print();