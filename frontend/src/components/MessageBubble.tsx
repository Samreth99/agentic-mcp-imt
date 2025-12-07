import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './MessageBubble.css';

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`message-bubble ${message.role}`}>
      <div className="message-content">
        <div className="message-text">
          {message.role === 'assistant' ? (
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({ children }) => <h1 className="md-h1">{children}</h1>,
                h2: ({ children }) => <h2 className="md-h2">{children}</h2>,
                h3: ({ children }) => <h3 className="md-h3">{children}</h3>,
                h4: ({ children }) => <h4 className="md-h4">{children}</h4>,
                p: ({ children }) => <p className="md-p">{children}</p>,
                ul: ({ children }) => <ul className="md-ul">{children}</ul>,
                ol: ({ children }) => <ol className="md-ol">{children}</ol>,
                li: ({ children }) => <li className="md-li">{children}</li>,
                blockquote: ({ children }) => <blockquote className="md-blockquote">{children}</blockquote>,
                code: ({ className, children, ...props }) => {
                  const isInline = !className;
                  return isInline ? (
                    <code className="md-code-inline" {...props}>{children}</code>
                  ) : (
                    <code className={`md-code-block ${className || ''}`} {...props}>{children}</code>
                  );
                },
                pre: ({ children }) => <pre className="md-pre">{children}</pre>,
                table: ({ children }) => (
                  <div className="md-table-wrapper">
                    <table className="md-table">{children}</table>
                  </div>
                ),
                thead: ({ children }) => <thead className="md-thead">{children}</thead>,
                tbody: ({ children }) => <tbody className="md-tbody">{children}</tbody>,
                tr: ({ children }) => <tr className="md-tr">{children}</tr>,
                th: ({ children }) => <th className="md-th">{children}</th>,
                td: ({ children }) => <td className="md-td">{children}</td>,
                a: ({ href, children }) => (
                  <a href={href} target="_blank" rel="noopener noreferrer" className="md-link">
                    {children}
                  </a>
                ),
                hr: () => <hr className="md-hr" />,
                strong: ({ children }) => <strong className="md-strong">{children}</strong>,
                em: ({ children }) => <em className="md-em">{children}</em>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          ) : (
            message.content
          )}
        </div>
        <div className="message-time">{formatTime(message.timestamp)}</div>
      </div>
    </div>
  );
};

export default MessageBubble;
