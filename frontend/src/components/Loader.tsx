import React from 'react';

interface LoaderProps {
    message?: string;
}

const Loader: React.FC<LoaderProps> = ({ message = 'Processing...' }) => {
    return (
        <div className="flex items-center justify-center gap-3 p-4">
            <div className="relative">
                <div className="w-8 h-8 border-4 border-emerald-200 rounded-full"></div>
                <div className="absolute top-0 left-0 w-8 h-8 border-4 border-emerald-500 rounded-full border-t-transparent animate-spin"></div>
            </div>
            <span className="text-gray-400 font-medium">{message}</span>
        </div>
    );
};

export default Loader;
