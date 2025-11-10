const speechRecognition = (window.SpeechRecognition || window.webkitSpeechRecognition)
const recognition = new speechRecognition()
const textbox = $("#textbox")
const instructions = $("#instructions")

recognition.continuous = true
let content = ''

recognition.onstart = function() {
    instructions.text("Voice Recognition is on")
}

recognition.onresult = function(event) {
    if (event.results.length) {
        textbox.val(content + event.results[event.results.length - 1][0].transcript);
        content = textbox.val();
        textbox[0].scrollTop = textbox[0].scrollHeight;
    }
}

recognition.onspeechend = function() {
    instructions.text("No activity")
}

recognition.onend = function() {
    instructions.text("Voice Recognition is off")
}

recognition.onerror = function(event) {
    if (event.error === 'no-speech') {
        instructions.text("No speech was detected. Try again.")
    }
}

$("#start-btn").click(function (event) {
    if ($(this).html() === 'Start') {
        content = '';
    }

    if ($(this).hasClass('stopped')) {
        recognition.stop();
    } else {
        recognition.start();
    }

    $(this)
      .toggleClass('stopped start')
      .html($(this).hasClass('stopped') ? 'Stop' : 'Start');
});

textbox.on('input', function(){
    content = $(this).val()
    $("#start-btn").html('Start').removeClass('started');
});


$(".custom-btn2").click(function() {
    window.open('http://192.168.228.232:8000', '_blank');
});


// New functionality

$(".custom-btn").click(async function() {
    const text = $("#textbox").val(); // Get the text from the textbox
    if (!text.trim()) {
        alert('Please enter some text before converting to gcode.');
        return;
    }
    
    const response = await fetch('http://127.0.0.1:5000/convert',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: text })
    });

    if (!response.ok) {
        alert('Error converting text to gcode. Please try again.');
        return;
    }

    const data = await response.json();
    displayGcode(data.gcode);
    // downloadFile(data.gcode);
});

function displayGcode(gcode) {
    const formattedGcode = gcode.join('\n');
    $("#gcodeBox").val(formattedGcode);
}

function downloadFile(content) {
    const formattedContent = content.join('\n');
    const blob = new Blob([formattedContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'output.gcode';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Event listener for the save button
$("#save-btn").click(function() {
    const gcodeContent = $("#gcodeBox").val();
    const blob = new Blob([gcodeContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    // Create a temporary anchor element and trigger the download
    const downloadLink = document.createElement('a');
    downloadLink.href = url;
    downloadLink.download = 'output.gcode';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    // Clean up by revoking the object URL
    URL.revokeObjectURL(url);
});