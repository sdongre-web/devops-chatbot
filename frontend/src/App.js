import React, { useState } from 'react';


function App() {
const [query, setQuery] = useState("");
const [messages, setMessages] = useState([]);


const sendQuery = async () => {
const resp = await fetch("http://localhost:8000/chat", {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ query })
});
const data = await resp.json();
setMessages([...messages, { role: "user", text: query }, { role: "bot", text: data.answer }]);
setQuery("");
};


return (
<div>
<h2>DevOps Chatbot</h2>
<div>
{messages.map((m, i) => (
<p key={i}><b>{m.role}:</b> {m.text}</p>
))}
</div>
<input value={query} onChange={e => setQuery(e.target.value)} />
<button onClick={sendQuery}>Send</button>
</div>
);
}


export default App;
