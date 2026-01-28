'use client';

import { useState, useEffect } from 'react';
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

                // Auto-select first available provider
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
            <div className="mb-8">
                <h1 className="text-xl font-bold text-[var(--color-primary)] flex items-center gap-2">
                    <span>Smart ATS</span>
                </h1>
                <p className="text-xs text-[var(--color-text-secondary)] mt-2">
                    AI-Powered CV Analysis
                </p>
            </div>

            <div className="mb-8">
                <h3 className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mt-2 mb-4">
                    AI Model Selection
                </h3>

                {loading ? (
                    <div className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
                        <div className="spinner"></div>
                        Loading models...
                    </div>
                ) : error ? (
                    <div className="alert alert-error text-xs">{error}</div>
                ) : (
                    <>
                        <div className="mb-4">
                            <label className="label text-xs">Provider</label>
                            <select
                                className="select"
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

                        <div className="mb-4">
                            <label className="label text-xs">Model</label>
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

            <div className="mb-8">
                <h3 className="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mt-2 mb-4">
                    Provider Status
                </h3>

                {modelStatus && (
                    <div className="space-y-2">
                        {Object.entries(modelStatus).map(([provider, status]) => (
                            <div
                                key={provider}
                                className={`flex items-center gap-2 text-xs px-3 py-2 rounded-lg font-medium ${status.available
                                    ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]'
                                    : 'bg-[var(--color-error-bg)] text-[var(--color-error)]'
                                    }`}
                            >
                                <span>{status.available ? '✅' : '❌'}</span>
                                {provider}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {selectedProvider && selectedModel && (
                <div className="p-4 bg-[var(--color-background)] rounded-lg border border-[var(--color-border)] mb-8">
                    <p className="text-xs text-[var(--color-text-secondary)] mb-2 font-medium">Current Selection:</p>
                    <p className="text-sm font-semibold text-[var(--color-text-primary)]">{selectedProvider}</p>
                    <p className="text-xs text-[var(--color-primary)] mt-1">{selectedModel}</p>
                </div>
            )}

            {/* Theme Toggle */}
            <div className="mt-auto pt-4 border-t border-[var(--color-border)]">
                <ThemeToggle />
            </div>
        </aside>
    );
}
