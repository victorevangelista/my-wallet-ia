document.addEventListener("DOMContentLoaded", function() {
    var chatHistory = document.getElementById("chat-history");
    if (chatHistory) {
        // Observa mudanças nos filhos do chat
        var observer = new MutationObserver(function() {
            chatHistory.scrollTop = chatHistory.scrollHeight;
        });
        observer.observe(chatHistory, { childList: true, subtree: true });
    }
});