import React from 'react';
import { Mail } from 'lucide-react';

interface EmailDraftProps {
    emailInput: string;
    setEmailInput: (val: string) => void;
    isDrafting: boolean;
    handleDraftEmail: () => Promise<void>;
    emailDraft: string | null;
}

const EmailDraft: React.FC<EmailDraftProps> = ({
    emailInput,
    setEmailInput,
    isDrafting,
    handleDraftEmail,
    emailDraft
}) => {
    return (
        <div className="space-y-4 pt-8 border-t border-light">
            <div className="flex items-center gap-3 text-lg font-semibold text-foreground">
                <Mail size={20} className="text-secondary-text" strokeWidth={2.5} />
                <h3>Draft Response Email</h3>
            </div>

            <div className="bg-surface rounded-2xl border border-light p-6 space-y-5 shadow-sm">
                <div className="space-y-2">
                    <label className="text-[10px] font-bold text-secondary-text uppercase tracking-widest pl-1">Additional message/concerns:</label>
                    <textarea
                        value={emailInput}
                        onChange={(e) => setEmailInput(e.target.value)}
                        className="w-full h-24 bg-muted border border-light rounded-xl p-4 text-sm text-foreground focus:outline-none focus:ring-4 focus:ring-primary/5 focus:border-primary transition-all resize-none font-medium placeholder:text-secondary-text/50"
                    />
                </div>

                <div className="flex justify-start">
                    <button
                        onClick={handleDraftEmail}
                        disabled={isDrafting}
                        className="flex items-center gap-2.5 bg-primary hover:bg-primary-hover disabled:bg-border-light text-white px-5 py-2.5 rounded-xl text-sm font-bold transition-all shadow-md active:scale-[0.98]"
                    >
                        {isDrafting ? (
                            <>
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                <span>Generating Transcript...</span>
                            </>
                        ) : (
                            <>
                                <Mail size={16} />
                                <span> Draft Email</span>
                            </>
                        )}
                    </button>
                </div>

                {emailDraft && (
                    <div className="mt-6 pt-6 border-t border-light">
                        <div className="flex items-center justify-between mb-3">
                            <h4 className="text-[10px] font-bold text-secondary-text uppercase tracking-widest pl-1">Email Draft</h4>
                        </div>
                        <div className="bg-muted border border-light rounded-2xl p-5 font-mono text-sm text-foreground whitespace-pre-wrap max-h-[300px] overflow-y-auto leading-relaxed">
                            {emailDraft}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default EmailDraft;
