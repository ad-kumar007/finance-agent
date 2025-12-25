import React from 'react';

interface ResponsePanelProps {
    question: string | null;
    answer: string | null;
    error: string | null;
    audioUrl?: string | null;
    suggestions?: string[];
}

const ResponsePanel: React.FC<ResponsePanelProps> = ({
    question,
    answer,
    error,
    audioUrl,
    suggestions,
}) => {
    if (!question && !answer && !error) {
        return null;
    }

    return (
        <div className="w-full mt-6">
            {error ? (
                <div className="p-6 bg-white border-2 border-red-500 rounded-2xl shadow-lg">
                    <div className="flex items-center gap-2 text-red-700 font-semibold mb-4">
                        <span>❌</span>
                        <span>Error</span>
                    </div>
                    <p className="text-gray-900">{error}</p>
                    {suggestions && suggestions.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-gray-300">
                            <p className="text-sm text-gray-700 font-semibold mb-2">Suggestions:</p>
                            <ul className="list-disc list-inside text-gray-900 text-sm">
                                {suggestions.map((s, i) => (
                                    <li key={i}>{s}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            ) : (
                <div className="p-6 bg-white border-2 border-emerald-500 rounded-2xl shadow-lg">
                    <div className="flex items-center gap-2 text-emerald-700 font-semibold mb-4">
                        <span>✅</span>
                        <span>Answer received!</span>
                    </div>

                    {question && (
                        <div className="mb-4">
                            <p className="text-sm text-gray-600 font-semibold mb-1">You asked:</p>
                            <p className="text-lg text-gray-900 font-medium">{question}</p>
                        </div>
                    )}

                    {answer && (
                        <div className="mb-4">
                            <p className="text-sm text-gray-600 font-semibold mb-2">Answer:</p>
                            <p className="text-gray-900 whitespace-pre-wrap leading-relaxed">{answer}</p>
                        </div>
                    )}

                    {audioUrl && (
                        <div className="mt-4 pt-4 border-t border-gray-300">
                            <p className="text-sm text-gray-700 font-semibold mb-2">🔊 Audio Response:</p>
                            <audio
                                controls
                                src={audioUrl}
                                className="w-full max-w-md"
                            >
                                Your browser does not support the audio element.
                            </audio>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default ResponsePanel;
