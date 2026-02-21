'use client';

import { useState, useEffect } from 'react';
import { Bot, Cpu, CheckCircle2, XCircle, ChevronDown, Layers } from 'lucide-react';
import { ModelStatus, getModels } from '@/lib/api';
import ThemeToggle from './ThemeToggle';

interface SidebarProps {
    selectedProvider: string;
    selectedModel: string;
    onProviderChange: (provider: string) => void;
    onModelChange: (model: string) => void;
}

export default function Sidebar({
    selectedProvider,
    selectedModel,
    onProviderChange,
    onModelChange,
}: SidebarProps) {
    const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchModels() {
            try {
                const status = await getModels();
                setModelStatus(status);
                const providers = Object.keys(status);
                const firstAvailable = providers.find(p => status[p].available);
                if (firstAvailable && !selectedProvider) {
                    onProviderChange(firstAvailable);
                    if (status[firstAvailable].models.length > 0) {
                        onModelChange(status[firstAvailable].models[0]);
                    }
                }
            } catch (err) {
                setError('Failed to connect to backend');
            } finally {
                setLoading(false);
            }
        }
        fetchModels();
    }, []);

    const availableProviders = modelStatus
        ? Object.keys(modelStatus).filter(p => modelStatus[p].available)
        : [];

    const availableModels = modelStatus && selectedProvider
        ? modelStatus[selectedProvider]?.models || []
        : [];

    return (
        <aside className="sidebar">
            {/* Logo / Brand */}
            <div className="mb-8">
                <div className="flex items-center gap-2.5 mb-1">
                    <div
                        className="w-9 h-9 rounded-xl flex items-center justify-center"
                        style={{ background: 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-hover) 100%)' }}
                    >
                        <Bot size={20} color="white" />
                    </div>
                    <div>
                        <h1 className="text-base font-bold" style={{ color: 'var(--color-primary)' }}>Smart ATS</h1>
                        <p className="text-[10px] text-[var(--color-text-secondary)] font-medium tracking-wider uppercase">
                            AI-Powered Analysis
                        </p>
                    </div>
                </div>
            </div>

            {/* AI Model Selection */}
            <div className="mb-6">
                <div className="section-divider">
                    <Cpu size={12} />
                    <span>AI Configuration</span>
                </div>

                {loading ? (
                    <div className="flex items-center gap-2.5 text-sm text-[var(--color-text-secondary)] py-4 justify-center">
                        <div className="spinner"></div>
                        <span>Loading models...</span>
                    </div>
                ) : error ? (
                    <div className="alert alert-error text-xs">{error}</div>
                ) : (
                    <>
                        <div className="mb-4">
                            <label className="label text-[11px]">
                                <Layers size={12} />
                                Provider
                            </label>
                            <div className="relative">
                                <select
                                    className="select"
                                    style={{ paddingRight: '2.5rem' }}
                                    value={selectedProvider}
                                    onChange={(e) => {
                                        onProviderChange(e.target.value);
                                        const models = modelStatus?.[e.target.value]?.models || [];
                                        if (models.length > 0) {
                                            onModelChange(models[0]);
                                        }
                                    }}
                                >
                                    {availableProviders.map(provider => (
                                        <option key={provider} value={provider}>{provider}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div className="mb-4">
                            <label className="label text-[11px]">
                                <Cpu size={12} />
                                Model
                            </label>
                            <select
                                className="select"
                                value={selectedModel}
                                onChange={(e) => onModelChange(e.target.value)}
                            >
                                {availableModels.map(model => (
                                    <option key={model} value={model}>{model}</option>
                                ))}
                            </select>
                        </div>
                    </>
                )}
            </div>

            {/* Provider Status */}
            <div className="mb-6">
                <div className="section-divider">
                    <span>Status</span>
                </div>

                {modelStatus && (
                    <div className="space-y-2">
                        {Object.entries(modelStatus).map(([provider, status]) => (
                            <div
                                key={provider}
                                className={`provider-pill ${status.available ? 'provider-pill-available' : 'provider-pill-unavailable'}`}
                            >
                                {status.available
                                    ? <CheckCircle2 size={14} />
                                    : <XCircle size={14} />
                                }
                                <span>{provider}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Current Selection Card */}
            {selectedProvider && selectedModel && (
                <div className="glass-card mb-6">
                    <p className="text-[10px] text-[var(--color-text-secondary)] font-semibold uppercase tracking-wider mb-2">Active Model</p>
                    <p className="text-sm font-bold text-[var(--color-text-primary)]">{selectedProvider}</p>
                    <p className="text-xs mt-0.5" style={{ color: 'var(--color-primary)' }}>{selectedModel}</p>
                </div>
            )}

            {/* Spacer */}
            <div className="flex-1"></div>

            {/* Theme Toggle */}
            <div className="pt-4 border-t border-[var(--color-border)]">
                <ThemeToggle />
            </div>
        </aside>
    );
}
