import React, { useState, useRef, useCallback } from 'react';

interface VoiceRecorderProps {
    onAudioReady: (audioBlob: Blob, filename: string) => void;
    isLoading: boolean;
}

const VoiceRecorder: React.FC<VoiceRecorderProps> = ({ onAudioReady, isLoading }) => {
    const [isRecording, setIsRecording] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
    const [audioUrl, setAudioUrl] = useState<string | null>(null);

    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const chunksRef = useRef<Blob[]>([]);
    const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const startRecording = useCallback(async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
            mediaRecorderRef.current = mediaRecorder;
            chunksRef.current = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    chunksRef.current.push(e.data);
                }
            };

            mediaRecorder.onstop = () => {
                const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
                setAudioBlob(blob);
                setAudioUrl(URL.createObjectURL(blob));
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
            setRecordingTime(0);

            timerRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1);
            }, 1000);
        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Could not access microphone. Please check permissions.');
        }
    }, []);

    const stopRecording = useCallback(() => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            if (timerRef.current) {
                clearInterval(timerRef.current);
                timerRef.current = null;
            }
        }
    }, [isRecording]);

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setAudioBlob(file);
            setAudioUrl(URL.createObjectURL(file));
        }
    };

    const handleSubmit = () => {
        if (audioBlob) {
            const filename = audioBlob instanceof File ? audioBlob.name : 'recording.webm';
            onAudioReady(audioBlob, filename);
        }
    };

    const clearRecording = () => {
        setAudioBlob(null);
        if (audioUrl) {
            URL.revokeObjectURL(audioUrl);
            setAudioUrl(null);
        }
        setRecordingTime(0);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const formatTime = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="w-full p-4 bg-white border border-gray-300 rounded-lg">
            <h3 className="text-sm font-medium text-gray-800 mb-4">🎙️ Ask via Audio</h3>

            <div className="flex flex-col gap-4">
                {/* Recording Controls */}
                <div className="flex items-center gap-3">
                    {!isRecording ? (
                        <button
                            onClick={startRecording}
                            disabled={isLoading || !!audioBlob}
                            className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center gap-2"
                        >
                            <span className="w-3 h-3 bg-white rounded-full"></span>
                            Record
                        </button>
                    ) : (
                        <button
                            onClick={stopRecording}
                            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2 animate-pulse"
                        >
                            <span className="w-3 h-3 bg-red-500 rounded-sm"></span>
                            Stop ({formatTime(recordingTime)})
                        </button>
                    )}

                    <span className="text-gray-500">or</span>

                    <label className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-lg transition-colors cursor-pointer">
                        Upload Audio
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".wav,.mp3,.m4a,.webm"
                            onChange={handleFileUpload}
                            disabled={isLoading || isRecording}
                            className="hidden"
                        />
                    </label>
                </div>

                {/* Audio Preview */}
                {audioUrl && (
                    <div className="flex flex-col gap-3 p-3 bg-gray-900 rounded-lg">
                        <audio controls src={audioUrl} className="w-full" />
                        <div className="flex gap-2">
                            <button
                                onClick={handleSubmit}
                                disabled={isLoading}
                                className="flex-1 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
                            >
                                {isLoading ? 'Processing...' : 'Get Answer (Audio)'}
                            </button>
                            <button
                                onClick={clearRecording}
                                disabled={isLoading}
                                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
                            >
                                Clear
                            </button>
                        </div>
                    </div>
                )}

                <p className="text-xs text-gray-500">
                    Supported formats: WAV, MP3, M4A, WebM
                </p>
            </div>
        </div>
    );
};

export default VoiceRecorder;
