import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, MessageCircle, Send, Info, ChevronDown, ChevronUp, Database, FileText } from 'lucide-react';
import { toast } from 'sonner';

interface ChatResponse {
  response: string;
  best_summary_file: string;
  schema_summary: string;
}

const DataQueryInterface = () => {
  const [question, setQuestion] = useState('');
  const [fullAnswer, setFullAnswer] = useState('');
  const [displayedAnswer, setDisplayedAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [responseData, setResponseData] = useState<ChatResponse | null>(null);
  const [showDetails, setShowDetails] = useState(false);

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
    setResponseData(null);

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
      setResponseData(data);
      setFullAnswer(data.response);
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
            <h1 className="text-4xl font-bold text-gray-800">AI Data Assistant</h1>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Ask questions about your data and get intelligent business insights powered by advanced LLM technology. 
            Simply describe what you want to know in natural language!
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
              <div className="flex items-center justify-between">
                <CardTitle className="text-xl text-gray-700 flex items-center gap-2">
                  <MessageCircle className="h-5 w-5" />
                  LLM Response
                </CardTitle>
                {responseData && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowDetails(!showDetails)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <Info className="h-4 w-4 mr-1" />
                    Details
                    {showDetails ? <ChevronUp className="h-4 w-4 ml-1" /> : <ChevronDown className="h-4 w-4 ml-1" />}
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="text-center space-y-4">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
                    <p className="text-gray-600">Analyzing your question and generating response with LLM...</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Main LLM Response */}
                  <div className="prose prose-blue prose-lg max-w-none text-gray-800 transition-all whitespace-pre-wrap">
                    <ReactMarkdown 
                      children={displayedAnswer} 
                      remarkPlugins={[remarkGfm]} 
                      rehypePlugins={[rehypeRaw]} 
                    />
                  </div>

                  {/* Response Details */}
                  {showDetails && responseData && (
                    <div className="mt-6 pt-4 border-t border-gray-200">
                      <div className="grid gap-4 md:grid-cols-2">
                        <Card className="bg-blue-50 border-blue-200">
                          <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-blue-800 flex items-center gap-2">
                              <Database className="h-4 w-4" />
                              Schema Source
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="pt-0">
                            <p className="text-xs text-blue-700 font-mono bg-blue-100 px-2 py-1 rounded">
                              {responseData.best_summary_file}
                            </p>
                          </CardContent>
                        </Card>

                        <Card className="bg-green-50 border-green-200">
                          <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-green-800 flex items-center gap-2">
                              <FileText className="h-4 w-4" />
                              Schema Context
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="pt-0">
                            <div className="text-xs text-green-700 max-h-32 overflow-y-auto bg-green-100 px-2 py-1 rounded">
                              {responseData.schema_summary.length > 200 
                                ? `${responseData.schema_summary.substring(0, 200)}...`
                                : responseData.schema_summary
                              }
                            </div>
                          </CardContent>
                        </Card>
                      </div>

                      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-600">
                          <strong>How it works:</strong> Your question was matched against our database schema using semantic search. 
                          The most relevant schema information was then sent to the LLM to generate a comprehensive business intelligence response.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Helpful Tips */}
        <Card className="mt-8 bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg text-green-800">💡 Tips for better LLM responses</CardTitle>
          </CardHeader>
          <CardContent className="text-green-700">
            <ul className="space-y-2 text-sm">
              <li>• Ask business-focused questions like "What are our top revenue drivers?"</li>
              <li>• Request analysis like "Show me trends in customer behavior"</li>
              <li>• Ask for strategic insights: "What should we focus on to increase profits?"</li>
              <li>• The AI will provide comprehensive business intelligence recommendations</li>
              <li>• Use the Details button to see how your question was processed</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DataQueryInterface;
