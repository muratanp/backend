import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Sparkles, Send, Bot, User } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function AIInsights() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your Xandeum Network AI assistant. I can help you analyze network data, find optimal nodes for staking, understand score breakdowns, and provide insights about network health. What would you like to know?',
    },
  ]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        role: 'assistant',
        content: 'This feature is coming soon! Once connected to a backend, I\'ll be able to analyze real-time network data, provide personalized staking recommendations, and answer questions about the Xandeum ecosystem.',
      };
      setMessages((prev) => [...prev, aiResponse]);
    }, 1000);
  };

  const suggestedQuestions = [
    'Which node has the best staking potential?',
    'What\'s the current network health status?',
    'Compare top 5 nodes by trust score',
    'Explain how node scores are calculated',
  ];

  return (
    <MainLayout>
      <div className="space-y-6 h-[calc(100vh-8rem)] flex flex-col">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Sparkles className="h-8 w-8 text-xand-purple" />
            AI Insights
          </h1>
          <p className="text-muted-foreground mt-1">
            Chat with AI to get insights about the Xandeum network
          </p>
        </div>

        {/* Chat Container */}
        <Card className="glass-card border-border flex-1 flex flex-col min-h-0">
          <CardContent className="flex-1 flex flex-col p-4 min-h-0">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 scrollbar-thin mb-4">
              {messages.map((message, idx) => (
                <div
                  key={idx}
                  className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : ''}`}
                >
                  {message.role === 'assistant' && (
                    <div className="h-8 w-8 rounded-lg bg-xand-purple/20 flex items-center justify-center shrink-0">
                      <Bot className="h-5 w-5 text-xand-purple" />
                    </div>
                  )}
                  <div
                    className={`rounded-lg p-3 max-w-[80%] ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>
                  {message.role === 'user' && (
                    <div className="h-8 w-8 rounded-lg bg-primary/20 flex items-center justify-center shrink-0">
                      <User className="h-5 w-5 text-primary" />
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Suggested Questions */}
            {messages.length <= 2 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {suggestedQuestions.map((question, idx) => (
                  <Button
                    key={idx}
                    variant="outline"
                    size="sm"
                    className="text-xs"
                    onClick={() => setInput(question)}
                  >
                    {question}
                  </Button>
                ))}
              </div>
            )}

            {/* Input */}
            <div className="flex gap-2">
              <Textarea
                placeholder="Ask about nodes, staking, network health..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                className="min-h-[44px] max-h-32 resize-none bg-muted border-border"
                rows={1}
              />
              <Button onClick={handleSend} disabled={!input.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
