import React, { useState } from 'react';

interface PromptBoxProps {
    onSubmit: (question: string) => void;
    isLoading: boolean;
    placeholder?: string;
}

const PromptBox: React.FC<PromptBoxProps> = ({
    onSubmit,
    isLoading,
    placeholder = 'Type your finance question...'
}) => {
    const [question, setQuestion] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (question.trim() && !isLoading) {
            onSubmit(question.trim());
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="w-full">
            <div className="flex flex-col gap-3">
                <label htmlFor="question" className="text-sm font-medium text-gray-800">
                    📝 Ask via Text
                </label>
                <div className="flex gap-3">
                    <input
                        id="question"
                        type="text"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={placeholder}
                        disabled={isLoading}
                        className="flex-1 px-4 py-3 bg-[#f5f5dc] border border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    />
                    <button
                        type="submit"
                        disabled={!question.trim() || isLoading}
                        className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                    >
                        {isLoading ? 'Thinking...' : 'Get Answer'}
                    </button>
                </div>
            </div>
        </form>
    );
};

export default PromptBox;
