import React, { useState, useRef, useCallback, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

const ChatWrapper = styled.div`
  display: flex;
  flex-direction: column;
  height: 70vh; /* Fixed height for the chat container */
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
`;

const ChatContainer = styled.div`
  flex-grow: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const Message = styled.div`
  padding: 12px 16px;
  border-radius: 8px;
  max-width: 80%;
  word-break: break-word;
  background-color: ${({ sender }) => (sender === 'user' ? '#007bff' : '#f1f1f1')};
  color: ${({ sender }) => (sender === 'user' ? '#fff' : '#333')};
  align-self: ${({ sender }) => (sender === 'user' ? 'flex-end' : 'flex-start')};
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const InputArea = styled.div`
  position: sticky;
  bottom: 0;
  background-color: #fff;
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
`;

const InputContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
`;

const InputField = styled.input`
  flex-grow: 1;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s ease;

  &:focus {
    border-color: #007bff;
  }
`;

const SendButton = styled.button`
  padding: 12px 20px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #0056b3;
  }

  &:disabled {
    background-color: #b0bec5;
    cursor: not-allowed;
  }
`;

const ChatInterface = ({ documentName }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatContainerRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = useCallback(async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput || isLoading) return;

    setMessages((prev) => [...prev, { id: Date.now(), text: trimmedInput, sender: 'user' }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.post('/query/', { question: trimmedInput });
      setMessages((prev) => [...prev, { id: Date.now(), text: response.data.answer, sender: 'bot' }]);
    } catch (error) {
      setMessages((prev) => [...prev, { id: Date.now(), text: 'Error: Could not get response', sender: 'bot' }]);
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading]);

  return (
    <ChatWrapper>
      <ChatContainer ref={chatContainerRef}>
        {messages.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#777', marginTop: '20px' }}>
            {documentName
              ? `Start chatting about "${documentName}"...`
              : 'Start a conversation...'}
          </div>
        ) : (
          messages.map((message) => (
            <Message key={message.id} sender={message.sender}>
              {message.text}
            </Message>
          ))
        )}
      </ChatContainer>
      <InputArea>
        <InputContainer>
          <InputField
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            disabled={isLoading}
          />
          <SendButton onClick={sendMessage} disabled={!input.trim() || isLoading}>
            {isLoading ? 'Sending...' : 'Send'}
          </SendButton>
        </InputContainer>
      </InputArea>
    </ChatWrapper>
  );
};

export default ChatInterface;