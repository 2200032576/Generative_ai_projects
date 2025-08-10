async function sendMessage() {
    let inputField = document.getElementById("user-input");
    let input = inputField.value.trim();
    if (!input) return;

    let chatBox = document.getElementById("chat-box");

    // Add user message
    let userMessage = document.createElement("div");
    userMessage.className = "user-message";
    userMessage.textContent = input;
    chatBox.appendChild(userMessage);

    // Add bot loading message
    let botMessage = document.createElement("div");
    botMessage.className = "bot-message";
    botMessage.textContent = "Thinking...";
    chatBox.appendChild(botMessage);

    chatBox.scrollTop = chatBox.scrollHeight;

    // Send request to Flask backend
    try {
        let res = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: input })
        });

        let data = await res.json();
        // FIX: Change 'data.reply' to 'data.response'
        botMessage.textContent = data.response;
    } catch (error) {
        botMessage.textContent = "Error connecting to AI 😢";
    }

    inputField.value = "";
}