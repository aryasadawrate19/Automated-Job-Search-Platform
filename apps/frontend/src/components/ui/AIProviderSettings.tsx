"use client";

import React, { useState } from 'react';
import { api } from '@/lib/api';
import { AiProviderEnum, ApiKeyRequest, AiProviderRequest } from '@shared/index';

export const AIProviderSettings: React.FC = () => {
  const [provider, setProvider] = useState<AiProviderEnum>(AiProviderEnum.ANTHROPIC);
  const [keys, setKeys] = useState({
    anthropic: '',
    gemini: '',
    openai: '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const handleSaveKey = async (providerName: string, keyName: keyof typeof keys) => {
    if (!keys[keyName]) {
      setMessage({ type: 'error', text: `Please enter a key for ${providerName}` });
      return;
    }
    setLoading(true);
    setMessage(null);
    try {
      const payload: ApiKeyRequest = { api_key: keys[keyName] };
      if (keyName === 'anthropic') await api.saveAnthropicKey(payload);
      if (keyName === 'gemini') await api.saveGeminiKey(payload);
      if (keyName === 'openai') await api.saveOpenaiKey(payload);
      
      setMessage({ type: 'success', text: `${providerName} key saved and encrypted successfully.` });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to save key' });
    } finally {
      setLoading(false);
    }
  };

  const handleSetProvider = async (newProvider: AiProviderEnum) => {
    setLoading(true);
    setMessage(null);
    try {
      const payload: AiProviderRequest = { ai_provider: newProvider };
      await api.setAiProvider(payload);
      setProvider(newProvider);
      setMessage({ type: 'success', text: `Default AI provider set to ${newProvider}.` });
    } catch (err: any) {
      if (err.message && err.message.includes('api_key_required')) {
        setMessage({ type: 'error', text: `Please save an API key for ${newProvider} before activating it.` });
      } else {
        setMessage({ type: 'error', text: err.message || 'Failed to update provider' });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[var(--stitch-surface)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-lg)] p-6">
      <h2 className="text-xl font-semibold text-[var(--stitch-typography-primary)] mb-2">AI Capabilities</h2>
      <p className="text-sm text-[var(--stitch-typography-secondary)] mb-6">
        Configure your preferred AI provider for cover letter generation and resume tips. Keys are stored with AES-256 encryption.
      </p>

      {message && (
        <div className={`p-4 mb-6 rounded text-sm ${message.type === 'success' ? 'bg-[var(--stitch-success)]/10 text-[var(--stitch-success)] border border-[var(--stitch-success)]/20' : 'bg-[var(--stitch-error)]/10 text-[var(--stitch-error)] border border-[var(--stitch-error)]/20'}`}>
          {message.text}
        </div>
      )}

      {/* Provider Selection */}
      <div className="mb-8">
        <h3 className="text-sm font-medium text-[var(--stitch-typography-primary)] mb-3">Active Provider</h3>
        <div className="flex gap-4">
          {[
            { id: AiProviderEnum.ANTHROPIC, label: 'Anthropic (Claude)' },
            { id: AiProviderEnum.GEMINI, label: 'Google Gemini' },
            { id: AiProviderEnum.OPENAI, label: 'OpenAI (GPT-4o)' },
          ].map(p => (
            <button
              key={p.id}
              onClick={() => handleSetProvider(p.id)}
              disabled={loading}
              className={`px-4 py-2 rounded-[var(--stitch-radius-md)] text-sm font-medium transition-colors border ${
                provider === p.id
                  ? 'bg-[var(--stitch-primary)]/10 border-[var(--stitch-primary)] text-[var(--stitch-primary)]'
                  : 'bg-[var(--stitch-surface-hover)] border-[var(--stitch-border)] text-[var(--stitch-typography-secondary)] hover:border-[var(--stitch-primary)]/50'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-6">
        {/* Anthropic Key */}
        <div>
          <label className="block text-sm font-medium text-[var(--stitch-typography-primary)] mb-2">Anthropic API Key</label>
          <div className="flex gap-3">
            <input 
              type="password" 
              placeholder="sk-ant-..." 
              value={keys.anthropic}
              onChange={e => setKeys(prev => ({...prev, anthropic: e.target.value}))}
              className="flex-1 bg-[var(--stitch-surface-hover)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-md)] px-4 py-2 text-sm text-[var(--stitch-typography-primary)] focus:outline-none focus:border-[var(--stitch-primary)]"
            />
            <button 
              onClick={() => handleSaveKey('Anthropic', 'anthropic')}
              disabled={loading}
              className="px-4 py-2 bg-[var(--stitch-surface-hover)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-md)] text-sm font-medium hover:bg-[var(--stitch-primary)]/10 hover:text-[var(--stitch-primary)] hover:border-[var(--stitch-primary)] transition-colors"
            >
              Save Key
            </button>
          </div>
        </div>

        {/* Gemini Key */}
        <div>
          <label className="block text-sm font-medium text-[var(--stitch-typography-primary)] mb-2">Gemini API Key</label>
          <div className="flex gap-3">
            <input 
              type="password" 
              placeholder="AIza..." 
              value={keys.gemini}
              onChange={e => setKeys(prev => ({...prev, gemini: e.target.value}))}
              className="flex-1 bg-[var(--stitch-surface-hover)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-md)] px-4 py-2 text-sm text-[var(--stitch-typography-primary)] focus:outline-none focus:border-[var(--stitch-primary)]"
            />
            <button 
              onClick={() => handleSaveKey('Gemini', 'gemini')}
              disabled={loading}
              className="px-4 py-2 bg-[var(--stitch-surface-hover)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-md)] text-sm font-medium hover:bg-[var(--stitch-primary)]/10 hover:text-[var(--stitch-primary)] hover:border-[var(--stitch-primary)] transition-colors"
            >
              Save Key
            </button>
          </div>
        </div>

        {/* OpenAI Key */}
        <div>
          <label className="block text-sm font-medium text-[var(--stitch-typography-primary)] mb-2">OpenAI API Key</label>
          <div className="flex gap-3">
            <input 
              type="password" 
              placeholder="sk-proj-..." 
              value={keys.openai}
              onChange={e => setKeys(prev => ({...prev, openai: e.target.value}))}
              className="flex-1 bg-[var(--stitch-surface-hover)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-md)] px-4 py-2 text-sm text-[var(--stitch-typography-primary)] focus:outline-none focus:border-[var(--stitch-primary)]"
            />
            <button 
              onClick={() => handleSaveKey('OpenAI', 'openai')}
              disabled={loading}
              className="px-4 py-2 bg-[var(--stitch-surface-hover)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-md)] text-sm font-medium hover:bg-[var(--stitch-primary)]/10 hover:text-[var(--stitch-primary)] hover:border-[var(--stitch-primary)] transition-colors"
            >
              Save Key
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
