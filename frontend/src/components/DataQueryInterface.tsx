import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, MessageCircle, Send } from 'lucide-react';
import { toast } from 'sonner';

interface ChatResponse {
  answer: string;
}

const DataQueryInterface = () => {
  const [question, setQuestion] = useState('');
  const [fullAnswer, setFullAnswer] = useState('');
  const [displayedAnswer, setDisplayedAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Typing animation effect
  useEffect(() => {
    if (!fullAnswer) return;

    let i = 0;
    const interval = setInterval(() => {
      setDisplayedAnswer(fullAnswer.slice(0, i));
      i++;
      if (i > fullAnswer.length) clearInterval(interval);
    }, 10); // speed of typing

    return () => clearInterval(interval);
  }, [fullAnswer]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!question.trim()) {
      toast.error('Please enter a question before asking!');
      return;
    }

    setIsLoading(true);
    setFullAnswer('');
    setDisplayedAnswer('');

    try {
      const response = await fetch('http://localhost:5000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: question.trim() }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();
      setFullAnswer(data.answer);
      toast.success('Got your answer!');
    } catch (error) {
      console.error('Error connecting to chatbot:', error);
      toast.error('Sorry, I couldn\'t connect to the data assistant. Make sure the server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center items-center gap-3 mb-4">
            <MessageCircle className="h-10 w-10 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-800">Ask Me About Your Data</h1>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Simply type your question about the database and I'll help you find the answers you need. 
            No technical knowledge required!
          </p>
        </div>

        {/* Main Query Interface */}
        <Card className="mb-6 shadow-lg border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="pb-4">
            <CardTitle className="text-xl text-gray-700 flex items-center gap-2">
              <MessageCircle className="h-5 w-5" />
              What would you like to know?
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="question" className="text-sm font-medium text-gray-700">
                  Type your question here:
                </label>
                <Textarea
                  id="question"
                  placeholder="e.g., What are the top-selling products?"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="min-h-[100px] text-base resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  disabled={isLoading}
                />
              </div>

              <Button 
                type="submit" 
                disabled={isLoading || !question.trim()}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white text-lg py-6 font-semibold transition-all duration-200 transform hover:scale-[1.02]"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Getting your answer...
                  </>
                ) : (
                  <>
                    <Send className="mr-2 h-5 w-5" />
                    Ask
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Answer Display */}
        {(displayedAnswer || isLoading) && (
          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl text-gray-700">Answer</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="text-center space-y-4">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
                    <p className="text-gray-600">Analyzing your question and searching the data...</p>
                  </div>
                </div>
              ) : (
                <div className="prose prose-blue prose-lg max-w-none text-gray-800 transition-all whitespace-pre-wrap">
                  <ReactMarkdown 
                    children={displayedAnswer} 
                    remarkPlugins={[remarkGfm]} 
                    rehypePlugins={[rehypeRaw]} 
                  />
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Helpful Tips */}
        <Card className="mt-8 bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg text-green-800">💡 Tips for better results</CardTitle>
          </CardHeader>
          <CardContent className="text-green-700">
            <ul className="space-y-2 text-sm">
              <li>• Ask specific questions like "What are our best-selling products?"</li>
              <li>• You can ask about database structure like "What tables do we have?"</li>
              <li>• Try questions about relationships: "How are customers connected to orders?"</li>
              <li>• Don't worry about technical terms - just ask naturally!</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DataQueryInterface;
