import React, { useState, useEffect } from 'react';
import './ChatWindow.css';
import icon from './icon.webp'; 

const ChatWindow = () => {
  const [step, setStep] = useState('prompt'); 
  const [link, setLink] = useState('');
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  // eslint-disable-next-line
  const [summary, setSummary] = useState('');
  const [typingTimeout, setTypingTimeout] = useState(null);

  useEffect(() => {
    if (link && step === 'loading') {
      handleLinkSubmit();
    }
  },
  // eslint-disable-next-line
  [link]);

  useEffect(() => {
    if (query && step === 'query') {
      if (typingTimeout) {
        clearTimeout(typingTimeout); //must clear the previous query
      }
      const timeoutId = setTimeout(() => {
        handleQuerySubmit();
      }, 10000); //wait for 10secs before submitting the query automatically.
      setTypingTimeout(timeoutId);
    }
  }, 
  // eslint-disable-next-line
  [query]);

  const handleLinkSubmit = async () => {
    setStep('loading');
    try {
      const response = await fetch('http://127.0.0.1:8000/load/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: link }),
      });

      if (response.ok) {
        const data = await response.json();
        setSummary(data.message);
        setChatHistory([
          ...chatHistory,
          { type: 'ai', text: 'Ready when you are, go ahead ask me questions about the contents of the link you just gave me.' }
        ]);
        setStep('query'); //change functionality to querying.
      } else {
        setStep('prompt');
        alert('Failed to load content. Please try again.');
      }
    } catch (error) {
      setStep('prompt');
      alert('Network error. Please try again.');
    }
  };

  const handleQuerySubmit = async () => {
    setChatHistory([...chatHistory, { type: 'user', text: query }]);
    setQuery(''); // Clear the input field
    setStep('loading');

    try {
      const response = await fetch('http://127.0.0.1:8000/query/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
      });

      if (response.ok) {
        const data = await response.json();
        setChatHistory([...chatHistory, { type: 'user', text: query }, { type: 'ai', text: data.response }]);
        setStep('query');
      } else {
        setStep('query');
        alert('Failed to retrieve response. Please try again.');
      }
    } catch (error) {
      setStep('query');
      alert('Network error. Please try again.');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && query) {
      clearTimeout(typingTimeout); //clear the debounce timeout
      handleQuerySubmit(); //on hitting enter, just submit.
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <img src={icon} alt="icon" className="header-icon" />
        <h1>Wot dis jutsu!?</h1>
      </div>
      <div className="chat-body">
        {chatHistory.map((message, index) => (
          <div key={index} className={`message ${message.type === 'user' ? 'user-message' : 'ai-message'}`}>
            <span className="message-text">{message.text}</span>
          </div>
        ))}

        {step === 'loading' && (
          <div className="message ai-message typing-animation">
            <span className="message-text">Loading...</span>
          </div>
        )}
      </div>
      <div className="chat-input">
        <input
          type="text"
          placeholder="Paste your link here..."
          value={link}
          onChange={(e) => {
            setLink(e.target.value);
            setStep('loading');
          }}
          disabled={step === 'loading'} //DO NOT ALLOW USER TO POST ANOTHER REQUEST WHILE WE CREATE EMBEDDINGS OF THE DOCUMENTS!
        />
        <input
          type="text"
          placeholder="Ask your query..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setStep('query');
          }}
          onKeyPress={handleKeyPress} 
          disabled={step === 'loading'} //query under process, prevent user from asking anything else.
        />
      </div>
    </div>
  );
};

export default ChatWindow;
