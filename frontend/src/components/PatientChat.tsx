import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { ScrollArea } from "./ui/scroll-area";
import { Avatar, AvatarFallback } from "./ui/avatar";
import type { Patient } from "./PatientDashboard";

interface Message {
  id: string;
  text: string;
  sender: "doctor" | "ai";
  timestamp: Date;
}

interface PatientChatProps {
  patient: Patient;
}

export function PatientChat({ patient }: PatientChatProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: `Hello Dr. Smith! I have all the information about ${patient.name}. What would you like to know?`,
      sender: "ai",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const getAIResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes("allergy") || lowerMessage.includes("allergies")) {
      return `${patient.name} has documented allergies to Penicillin and Sulfa drugs. These should be avoided in any treatment plans.`;
    }
    
    if (lowerMessage.includes("medication") || lowerMessage.includes("drugs")) {
      return `${patient.name} is currently on: Metformin 500mg (twice daily), Lisinopril 10mg (once daily), and Aspirin 81mg (once daily).`;
    }
    
    if (lowerMessage.includes("history") || lowerMessage.includes("condition")) {
      return `${patient.name} has a history of Type 2 Diabetes and Hypertension. They're being treated for ${patient.condition}. Recent vitals show HR: ${patient.vitals.heartRate} bpm, BP: ${patient.vitals.bloodPressure}, Temp: ${patient.vitals.temperature}°C.`;
    }
    
    if (lowerMessage.includes("lab") || lowerMessage.includes("test")) {
      return "Recent lab results from Nov 10: Blood Glucose at 145 mg/dL (High), HbA1c at 7.2% (Elevated). Blood pressure today is 140/90 (High). Would you like me to order new tests?";
    }
    
    if (lowerMessage.includes("vital") || lowerMessage.includes("vitals")) {
      return `Current vitals for ${patient.name}: Heart Rate: ${patient.vitals.heartRate} bpm, Blood Pressure: ${patient.vitals.bloodPressure}, Temperature: ${patient.vitals.temperature}°C. These are being monitored continuously.`;
    }
    
    if (lowerMessage.includes("recommend") || lowerMessage.includes("suggest") || lowerMessage.includes("treatment")) {
      return `Based on ${patient.name}'s condition (${patient.condition}) and medical history, I recommend: 1) Continue monitoring vitals closely, 2) Consider adjusting blood pressure medication, 3) Order cardiac enzyme tests given the current symptoms. Would you like me to prepare these orders?`;
    }

    if (lowerMessage.includes("previous") || lowerMessage.includes("visit")) {
      return `${patient.name}'s most recent visits: Oct 15 - Annual checkup with Dr. Johnson, Aug 22 - Blood pressure check with you, Jun 10 - Diabetes management with Dr. Johnson.`;
    }
    
    return `I can help you with information about ${patient.name}'s medical history, allergies, medications, lab results, or treatment recommendations. What specific information do you need?`;
  };

  const handleSend = () => {
    if (!inputValue.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: "doctor",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newMessage]);
    const userInput = inputValue;
    setInputValue("");

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: getAIResponse(userInput),
        sender: "ai",
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, aiMessage]);
    }, 800);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickQuestions = [
    "What are the allergies?",
    "Show current medications",
    "Recent lab results",
    "Treatment recommendations",
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t shadow-2xl">
      <div className="container mx-auto">
        {/* Chat Header */}
        <div className="px-6 py-3 border-b bg-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-600" />
            <h3>AI Medical Assistant - {patient.name}</h3>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2"
          >
            {isExpanded ? (
              <>
                <ChevronDown className="w-4 h-4" />
                Minimize
              </>
            ) : (
              <>
                <ChevronUp className="w-4 h-4" />
                Expand
              </>
            )}
          </Button>
        </div>

        {isExpanded && (
          <>
            {/* Quick Questions */}
            <div className="px-6 pt-4 pb-2 border-b bg-slate-50">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-4 h-4 text-blue-600" />
                <p className="text-slate-600">Quick questions:</p>
              </div>
              <div className="flex gap-2 flex-wrap">
                {quickQuestions.map((question, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setInputValue(question);
                      setTimeout(() => handleSend(), 100);
                    }}
                    className="text-xs"
                  >
                    {question}
                  </Button>
                ))}
              </div>
            </div>

            {/* Messages Area */}
            <ScrollArea className="h-[250px] px-6 py-4">
              <div className="space-y-4" ref={scrollRef}>
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3 ${message.sender === "doctor" ? "justify-end" : "justify-start"}`}
                  >
                    {message.sender === "ai" && (
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-blue-100 text-blue-600">
                          <Sparkles className="w-4 h-4" />
                        </AvatarFallback>
                      </Avatar>
                    )}
                    <div
                      className={`max-w-[70%] rounded-lg p-3 ${
                        message.sender === "doctor"
                          ? "bg-blue-600 text-white"
                          : "bg-slate-100 text-slate-900"
                      }`}
                    >
                      <p className="break-words">{message.text}</p>
                      <p
                        className={`text-xs mt-1 ${
                          message.sender === "doctor" ? "text-blue-100" : "text-slate-500"
                        }`}
                      >
                        {message.timestamp.toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                    {message.sender === "doctor" && (
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-slate-700 text-white">DS</AvatarFallback>
                      </Avatar>
                    )}
                  </div>
                ))}
              </div>
            </ScrollArea>

            {/* Input Area */}
            <div className="px-6 py-4 border-t bg-white">
              <div className="flex gap-3">
                <Input
                  placeholder={`Ask me anything about ${patient.name}...`}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="flex-1"
                />
                <Button
                  onClick={handleSend}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Send className="w-4 h-4 mr-2" />
                  Send
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}