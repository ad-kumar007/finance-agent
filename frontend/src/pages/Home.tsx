import React, { useState, useRef, useEffect } from 'react';
import { PromptBox, ResponsePanel, VoiceRecorder, Loader } from '../components';
import { askQuestion, askAudio, getAudioUrl } from '../api/endpoints';

interface ResponseState {
    question: string | null;
    answer: string | null;
    error: string | null;
    audioUrl: string | null;
    suggestions?: string[];
}

const Home: React.FC = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [response, setResponse] = useState<ResponseState>({
        question: null,
        answer: null,
        error: null,
        audioUrl: null,
    });
    const responseRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to response when answer is received
    useEffect(() => {
        if ((response.answer || response.error) && responseRef.current) {
            setTimeout(() => {
                responseRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
    }, [response.answer, response.error]);

    const handleTextSubmit = async (question: string) => {
        setIsLoading(true);
        setResponse({ question: null, answer: null, error: null, audioUrl: null });
        const result = await askQuestion(question);
        if (result.error) {
            setResponse({ question, answer: null, error: result.error, audioUrl: null });
        } else if (result.data) {
            setResponse({
                question: result.data.question,
                answer: result.data.answer,
                error: result.data.error || null,
                audioUrl: null,
                suggestions: result.data.suggestions,
            });
        }
        setIsLoading(false);
    };

    const handleAudioSubmit = async (audioBlob: Blob, filename: string) => {
        setIsLoading(true);
        setResponse({ question: null, answer: null, error: null, audioUrl: null });
        const result = await askAudio(audioBlob, filename);
        if (result.error) {
            setResponse({ question: null, answer: null, error: result.error, audioUrl: null });
        } else if (result.data) {
            const audioUrl = result.data.answer_audio_file ? getAudioUrl(result.data.answer_audio_file) : null;
            setResponse({
                question: result.data.question,
                answer: result.data.answer,
                error: result.data.error || null,
                audioUrl,
            });
        }
        setIsLoading(false);
    };

    return (
        <div className="min-h-screen bg-white relative overflow-hidden">
            {/* Subtle Background Pattern */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#f0f0f0_1px,transparent_1px),linear-gradient(to_bottom,#f0f0f0_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-40"></div>

            {/* Gradient Accents */}
            <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-100 rounded-full blur-3xl opacity-30"></div>
            <div className="absolute bottom-0 left-0 w-96 h-96 bg-cyan-100 rounded-full blur-3xl opacity-30"></div>

            {/* Header */}
            <header className="border-b border-gray-200 bg-white/80 backdrop-blur-xl sticky top-0 z-50 shadow-sm">
                <div className="max-w-7xl mx-auto px-6 py-5">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-gradient-to-br from-emerald-500 to-cyan-600 rounded-xl flex items-center justify-center shadow-lg">
                                <span className="text-2xl">📈</span>
                            </div>
                            <div>
                                <h1 className="text-3xl font-black bg-gradient-to-r from-emerald-600 to-cyan-600 bg-clip-text text-transparent">
                                    MARKET PULSE
                                </h1>
                                <p className="text-xs text-gray-500 font-semibold tracking-wider">AI TRADING ASSISTANT</p>
                            </div>
                        </div>
                        <div className="hidden md:flex items-center gap-3 px-5 py-2.5 bg-emerald-50 rounded-full border border-emerald-200">
                            <div className="relative">
                                <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-ping absolute"></div>
                                <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full"></div>
                            </div>
                            <span className="text-emerald-700 text-sm font-bold tracking-wide">LIVE DATA</span>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-6 py-10 relative z-10">
                <div className="space-y-8">
                    {/* Stats Dashboard */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10">
                        {[
                            { icon: '🌐', value: '150+', label: 'Global Markets', color: 'from-emerald-500 to-emerald-600' },
                            { icon: '⚡', value: 'Real-Time', label: 'Live Prices', color: 'from-cyan-500 to-cyan-600' },
                            { icon: '🤖', value: 'AI', label: 'Powered', color: 'from-purple-500 to-purple-600' },
                            { icon: '🎯', value: '24/7', label: 'Available', color: 'from-pink-500 to-pink-600' },
                        ].map((stat, i) => (
                            <div key={i} className="bg-white p-6 rounded-2xl border border-gray-200 shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300">
                                <div className="text-4xl mb-3">{stat.icon}</div>
                                <div className={`text-3xl font-black bg-gradient-to-r ${stat.color} bg-clip-text text-transparent mb-1`}>{stat.value}</div>
                                <div className="text-xs font-semibold text-gray-600 uppercase tracking-wider">{stat.label}</div>
                            </div>
                        ))}
                    </div>

                    {/* Hero Section */}
                    <div className="text-center mb-12 space-y-6">
                        <div className="inline-flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-emerald-50 to-cyan-50 rounded-full border border-emerald-200">
                            <span className="text-2xl">💹</span>
                            <span className="text-emerald-700 font-bold text-sm">STOCKS • INDICES • REAL-TIME DATA</span>
                        </div>
                        <h2 className="text-5xl md:text-6xl font-black text-gray-900 leading-tight">
                            Ask. Analyze. <span className="bg-gradient-to-r from-emerald-600 to-cyan-600 bg-clip-text text-transparent">Trade Smarter.</span>
                        </h2>
                        <p className="text-gray-600 text-xl max-w-3xl mx-auto leading-relaxed">
                            Get instant insights on any stock or index. Powered by Yahoo Finance and advanced AI.
                        </p>
                    </div>

                    {/* Text Input Section */}
                    <section className="bg-white border border-gray-200 rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-500">
                        <PromptBox
                            onSubmit={handleTextSubmit}
                            isLoading={isLoading}
                            placeholder="e.g., What's the current price of Tesla? Show me NIFTY 50 today..."
                        />
                    </section>

                    {/* Voice Input Section */}
                    <section className="hover:scale-[1.01] transition-transform duration-300">
                        <VoiceRecorder onAudioReady={handleAudioSubmit} isLoading={isLoading} />
                    </section>

                    {/* Loading Indicator */}
                    {isLoading && (
                        <div className="flex justify-center py-8">
                            <div className="bg-white px-8 py-4 rounded-2xl border border-emerald-200 shadow-xl">
                                <Loader message="📊 Fetching market data..." />
                            </div>
                        </div>
                    )}

                    {/* Response Display */}
                    <div ref={responseRef}>
                        <ResponsePanel
                            question={response.question}
                            answer={response.answer}
                            error={response.error}
                            audioUrl={response.audioUrl}
                            suggestions={response.suggestions}
                        />
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="border-t border-gray-200 mt-20 bg-white/80 backdrop-blur-xl">
                <div className="max-w-7xl mx-auto px-6 py-8">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                        <div className="text-gray-600 text-sm">
                            <span className="font-bold bg-gradient-to-r from-emerald-600 to-cyan-600 bg-clip-text text-transparent">MARKET PULSE</span>
                            <span className="mx-2">•</span>
                            <span>Powered by Yahoo Finance & OpenRouter AI</span>
                        </div>
                        <div className="flex items-center gap-4 text-gray-500 text-sm">
                            <span className="hover:text-emerald-600 transition-colors cursor-pointer">Docs</span>
                            <span>•</span>
                            <span className="hover:text-cyan-600 transition-colors cursor-pointer">API</span>
                            <span>•</span>
                            <span className="hover:text-purple-600 transition-colors cursor-pointer">Support</span>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default Home;
