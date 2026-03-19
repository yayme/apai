document.getElementById('chat-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const userQuery = document.getElementById('user_query').value;
    fetch('/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({user_query: userQuery})
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById('response-block').innerHTML =
            "<div class='response-block'><b>Response:</b><br><pre>" + data.response + "</pre></div>";
        let historyHtml = "<div class='chat-history'>";
        data.history.forEach(entry => {
            historyHtml += "<div class='chat-entry'><div class='chat-q'><b>Q:</b> " + entry.question +
                "</div><div class='chat-a'><b>A:</b> " + entry.response + "</div></div>";
        });
        historyHtml += "</div>";
        document.getElementById('history-block').innerHTML = historyHtml;
        document.getElementById('user_query').value = "";
    });
});
