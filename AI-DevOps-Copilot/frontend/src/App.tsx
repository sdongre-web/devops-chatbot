import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Zap, Code, Terminal, Copy, Check } from "lucide-react";

// Markdown Parser Component
const MarkdownRenderer = ({ content }) => {
  const [copiedIndex, setCopiedIndex] = useState(null);

  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const parseMarkdown = (text) => {
    const elements = [];
    const lines = text.split('\n');
    let i = 0;
    let codeBlockIndex = 0;

    while (i < lines.length) {
      const line = lines[i];

      // Code blocks
      if (line.trim().startsWith('```')) {
        const language = line.trim().slice(3).trim();
        const codeLines = [];
        i++;
        while (i < lines.length && !lines[i].trim().startsWith('```')) {
          codeLines.push(lines[i]);
          i++;
        }
        const codeContent = codeLines.join('\n');
        const currentIndex = codeBlockIndex;
        elements.push(
          <div key={`code-${elements.length}`} className="my-4 rounded-lg overflow-hidden border border-slate-600">
            <div className="bg-slate-900 px-4 py-2 flex items-center justify-between border-b border-slate-600">
              <span className="text-xs text-cyan-400 font-mono">{language || 'code'}</span>
              <button
                onClick={() => copyToClipboard(codeContent, currentIndex)}
                className="flex items-center gap-1 text-xs text-slate-400 hover:text-cyan-400 transition-colors"
              >
                {copiedIndex === currentIndex ? (
                  <>
                    <Check className="w-3 h-3" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
            <pre className="bg-slate-950 p-4 overflow-x-auto">
              <code className="text-sm text-slate-200 font-mono leading-relaxed">
                {codeContent}
              </code>
            </pre>
          </div>
        );
        codeBlockIndex++;
        i++;
        continue;
      }

      // Headers
      if (line.startsWith('### ')) {
        elements.push(
          <h3 key={`h3-${elements.length}`} className="text-lg font-bold text-cyan-400 mt-5 mb-2">
            {line.slice(4)}
          </h3>
        );
        i++;
        continue;
      }

      if (line.startsWith('## ')) {
        elements.push(
          <h2 key={`h2-${elements.length}`} className="text-xl font-bold text-cyan-300 mt-6 mb-3">
            {line.slice(3)}
          </h2>
        );
        i++;
        continue;
      }

      if (line.startsWith('# ')) {
        elements.push(
          <h1 key={`h1-${elements.length}`} className="text-2xl font-bold text-white mt-6 mb-3">
            {line.slice(2)}
          </h1>
        );
        i++;
        continue;
      }

      // Bullet lists
      if (line.trim().startsWith('• ') || line.trim().startsWith('* ') || line.trim().startsWith('- ')) {
        const listItems = [];
        while (i < lines.length && (lines[i].trim().startsWith('• ') || lines[i].trim().startsWith('* ') || lines[i].trim().startsWith('- '))) {
          const itemText = lines[i].trim().slice(2);
          listItems.push(itemText);
          i++;
        }
        elements.push(
          <ul key={`ul-${elements.length}`} className="my-3 space-y-2 pl-5">
            {listItems.map((item, idx) => (
              <li key={idx} className="text-slate-200 leading-relaxed flex">
                <span className="text-cyan-400 mr-2">•</span>
                <span dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(item) }} />
              </li>
            ))}
          </ul>
        );
        continue;
      }

      // Numbered lists
      if (/^\d+\.\s/.test(line.trim())) {
        const listItems = [];
        while (i < lines.length && /^\d+\.\s/.test(lines[i].trim())) {
          const itemText = lines[i].trim().replace(/^\d+\.\s/, '');
          listItems.push(itemText);
          i++;
        }
        elements.push(
          <ol key={`ol-${elements.length}`} className="my-3 space-y-2 pl-5 list-decimal">
            {listItems.map((item, idx) => (
              <li key={idx} className="text-slate-200 leading-relaxed ml-4" dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(item) }} />
            ))}
          </ol>
        );
        continue;
      }

      // Empty lines
      if (line.trim() === '') {
        elements.push(<div key={`br-${elements.length}`} className="h-2" />);
        i++;
        continue;
      }

      // Regular paragraphs
      elements.push(
        <p key={`p-${elements.length}`} className="text-slate-200 leading-relaxed my-2" dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(line) }} />
      );
      i++;
    }

    return elements;
  };

  const formatInlineMarkdown = (text) => {
    // Bold
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong class="font-bold text-white">$1</strong>');
    
    // Inline code
    text = text.replace(/`([^`]+)`/g, '<code class="bg-slate-900 text-cyan-400 px-1.5 py-0.5 rounded text-sm font-mono">$1</code>');
    
    // Italic
    text = text.replace(/\*(.+?)\*/g, '<em class="italic text-slate-300">$1</em>');
    
    return text;
  };

  return <div className="markdown-content">{parseMarkdown(content)}</div>;
};

function App() {
  const [messages, setMessages] = useState([
    {
      type: "bot",
      text: "Hey there! 👋 I'm your DevOps Copilot. Whether it's CI/CD, containers, cloud infrastructure, or deployment strategies - I've got your back. What's on your mind?",
      timestamp: new Date(),
      source: "system"
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const askQuestion = async () => {
    if (!input.trim()) return;

    const userMessage = {
      type: "user",
      text: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const question = input;
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://10.50.70.106:8000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          question: question,
          top_k: 3
        })
      });

      const data = await res.json();

      const botMessage = {
        type: "bot",
        text: data.answer,
        timestamp: new Date(),
        source: data.source || "database"
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      const errorMessage = {
        type: "bot",
        text: `Oops! I couldn't connect to the knowledge base. ${err.message}\n\nPlease check if the backend server is running on port 8000.`,
        timestamp: new Date(),
        source: "error"
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  };

  const handleQuickTopic = (topic) => {
    setInput(topic);
  };

  const getSourceBadge = (source) => {
    const badges = {
      database: {
        color: "bg-green-500",
        icon: "📚",
        text: "Internal Knowledge Base"
      },
      llm_knowledge: {
        color: "bg-yellow-500",
        icon: "🤖",
        text: "AI General Knowledge"
      },
      error: {
        color: "bg-red-500",
        icon: "❌",
        text: "Connection Error"
      }
    };

    return badges[source] || badges.database;
  };

  return (
    <div className="h-screen w-full bg-slate-950 flex flex-col md:flex-row overflow-hidden fixed inset-0">
      {/* Sidebar */}
      <div className="w-80 bg-slate-900 border-r border-slate-800 p-6 flex flex-col">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-gradient-to-br from-cyan-500 to-blue-600 p-2.5 rounded-xl">
              <Terminal className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">DevOps Copilot</h1>
              <div className="flex items-center gap-1.5 text-cyan-400 text-sm">
                <Zap className="w-3 h-3" />
                <span>AI-Powered</span>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-3 flex-1">
          <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
            <div className="flex items-center gap-2 text-cyan-400 mb-2">
              <Code className="w-4 h-4" />
              <span className="font-semibold text-sm">Quick Topics</span>
            </div>
            <div className="space-y-2 text-sm text-slate-300">
              <div onClick={() => handleQuickTopic("How do I set up a CI/CD pipeline?")} className="hover:text-cyan-400 cursor-pointer transition-colors">→ CI/CD Pipelines</div>
              <div onClick={() => handleQuickTopic("Explain Docker containers and orchestration")} className="hover:text-cyan-400 cursor-pointer transition-colors">→ Docker & Kubernetes</div>
              <div onClick={() => handleQuickTopic("Best practices for cloud infrastructure")} className="hover:text-cyan-400 cursor-pointer transition-colors">→ Cloud Infrastructure</div>
              <div onClick={() => handleQuickTopic("How to implement monitoring and logging?")} className="hover:text-cyan-400 cursor-pointer transition-colors">→ Monitoring & Logging</div>
              <div onClick={() => handleQuickTopic("DevOps security best practices")} className="hover:text-cyan-400 cursor-pointer transition-colors">→ Security Best Practices</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-cyan-500/10 to-blue-600/10 rounded-xl p-4 border border-cyan-500/20">
            <p className="text-xs text-slate-400 leading-relaxed">
              💡 <span className="text-cyan-400 font-semibold">Pro Tip:</span> Ask me about deployment strategies, infrastructure as code, or troubleshooting production issues!
            </p>
          </div>
        </div>

        <div className="mt-auto pt-4 border-t border-slate-800">
          <div className="flex items-center gap-2 text-slate-500 text-xs">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Connected & Ready</span>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-slate-900 border-b border-slate-800 px-8 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-white">Chat Session</h2>
              <p className="text-sm text-slate-400">Ask anything about DevOps, CI/CD, Cloud & more</p>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg border border-slate-700">
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-slate-300">AI Active</span>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-4 ${msg.type === "user" ? "flex-row-reverse" : "flex-row"} animate-fadeIn`}
            >
              {/* Avatar */}
              <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center ${
                msg.type === "user" 
                  ? "bg-gradient-to-br from-purple-500 to-pink-600" 
                  : "bg-gradient-to-br from-cyan-500 to-blue-600"
              }`}>
                {msg.type === "user" ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
              </div>

              {/* Message */}
              <div className={`flex flex-col max-w-[75%] ${msg.type === "user" ? "items-end" : "items-start"}`}>
                <div className={`px-5 py-3.5 rounded-2xl ${
                  msg.type === "user"
                    ? "bg-gradient-to-br from-purple-500 to-pink-600 text-white"
                    : "bg-slate-800 text-slate-100 border border-slate-700"
                }`}>
                  {msg.type === "user" ? (
                    <p className="whitespace-pre-wrap leading-relaxed text-[15px]">{msg.text}</p>
                  ) : (
                    <MarkdownRenderer content={msg.text} />
                  )}
                  
                  {/* Source Badge */}
                  {msg.type === "bot" && msg.source && msg.source !== "system" && (
                    <div className="mt-3 pt-3 border-t border-slate-700">
                      <div className="flex items-center gap-2">
                        <div className={`w-1.5 h-1.5 ${getSourceBadge(msg.source).color} rounded-full`}></div>
                        <span className="text-xs text-slate-400">
                          {getSourceBadge(msg.source).icon} Source: {getSourceBadge(msg.source).text}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
                <span className="text-xs text-slate-500 mt-1.5 px-1">
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-4 animate-fadeIn">
              <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-slate-800 border border-slate-700 rounded-2xl px-5 py-3.5">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                  <span className="text-slate-400 text-sm ml-1">Analyzing...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-slate-900 border-t border-slate-800 p-6">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your DevOps question here..."
                  disabled={loading}
                  className="w-full px-5 py-4 bg-slate-800 text-white placeholder-slate-500 rounded-xl border-2 border-slate-700 focus:border-cyan-500 focus:outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed text-[15px]"
                />
              </div>
              <button
                onClick={askQuestion}
                disabled={loading || !input.trim()}
                className="bg-gradient-to-br from-cyan-500 to-blue-600 text-white px-8 py-4 rounded-xl hover:shadow-lg hover:shadow-cyan-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-semibold"
              >
                <Send className="w-5 h-5" />
                Send
              </button>
            </div>
            <p className="text-xs text-slate-500 mt-3 text-center">
              Press <kbd className="px-2 py-0.5 bg-slate-800 rounded border border-slate-700">Enter</kbd> to send • <kbd className="px-2 py-0.5 bg-slate-800 rounded border border-slate-700">Shift + Enter</kbd> for new line
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.4s ease-out;
        }

        .overflow-y-auto::-webkit-scrollbar {
          width: 10px;
        }

        .overflow-y-auto::-webkit-scrollbar-track {
          background: #0f172a;
        }

        .overflow-y-auto::-webkit-scrollbar-thumb {
          background: #334155;
          border-radius: 5px;
        }

        .overflow-y-auto::-webkit-scrollbar-thumb:hover {
          background: #475569;
        }
      `}</style>
    </div>
  );
}

export default App;
