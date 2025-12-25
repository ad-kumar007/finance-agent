/**
 * API Endpoints for Finance Assistant
 * Maps to EXACT backend routes used by Streamlit
 */

import { post, postFormData, get, getAudioUrl } from './client';

// ============ Response Types ============

export interface TextQuestionResponse {
    question: string;
    answer: string;
    error?: string;
    suggestions?: string[];
}

export interface AudioQuestionResponse {
    question: string;
    answer: string;
    answer_audio_file: string;
    error?: string;
}

export interface HealthCheckResponse {
    status: string;
    service: string;
}

// ============ API Functions ============

/**
 * Health check endpoint
 * GET /
 */
export async function healthCheck() {
    return get<HealthCheckResponse>('/');
}

/**
 * Ask a text question to the LLM
 * POST /ask_llm
 * Body: { question: string }
 * Response: { question, answer } or { error }
 */
export async function askQuestion(question: string) {
    return post<TextQuestionResponse>('/ask_llm', { question });
}

/**
 * Ask a question via audio upload
 * POST /ask_audio
 * Body: FormData with audio_file
 * Response: { question, answer, answer_audio_file } or { error }
 */
export async function askAudio(audioFile: File | Blob, filename: string = 'audio.wav') {
    const formData = new FormData();
    formData.append('audio_file', audioFile, filename);
    return postFormData<AudioQuestionResponse>('/ask_audio', formData);
}

/**
 * Get audio file URL for playback
 * GET /audio/{filename}
 */
export { getAudioUrl };
