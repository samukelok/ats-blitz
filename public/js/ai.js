import Groq from "groq-sdk";
const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

// Listen for the click event on the floating chat button
document.getElementById('openChat').addEventListener('click', async function(e) {
    e.preventDefault(); 
    openChatModal();

    const chatCompletion = await getGroqChatCompletion();
    console.log(chatCompletion.choices[0]?.message?.content || "");
});

// Function to open a modal or chat interface
function openChatModal() {
    let modalHtml = `
    <div id="chatModal" class="modal" style="display: block;">
        <div class="modal-content">
            <span class="close" onclick="closeChatModal()">×</span>
            <div id="chat-box">
                <div class="chat-history"></div>
                <textarea id="user-input" placeholder="Type your message..."></textarea>
                <button id="send-message">Send</button>
            </div>
        </div>
    </div>
    `;

    // Append the modal HTML to the body
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Handle the sending of a message
    document.getElementById('send-message').addEventListener('click', async () => {
        let userInput = document.getElementById('user-input').value;
        if (userInput.trim() !== "") {
            await handleUserMessage(userInput);  
            document.getElementById('user-input').value = '';  
        }
    });
}

// Function to handle the user message (interact with the AI service)
async function handleUserMessage(message) {
    const chatCompletion = await getGroqChatCompletion(message);
    const aiMessage = chatCompletion.choices[0]?.message?.content || "Sorry, I couldn't get a response.";
    
    // Append AI response to chat history
    const chatHistory = document.querySelector('.chat-history');
    chatHistory.innerHTML += `<div class="chat-message bot-message">${aiMessage}</div>`;
}

// Function to close the chat modal
function closeChatModal() {
    document.getElementById('chatModal').remove();
}

// Function to get Groq Chat Completion (you may modify this)
export async function getGroqChatCompletion(userMessage) {
    return groq.chat.completions.create({
        messages: [
            {
                role: "user",
                content: userMessage || "Explain the importance of fast language models",
            },
        ],
        model: "llama-3.3-70b-versatile",
    });
}