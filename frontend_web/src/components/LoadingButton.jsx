import React from 'react';

export default function LoadingButton({ isLoading, children, className = '', ...props }) {
  return (
    <button
      {...props}
      disabled={isLoading || props.disabled}
      className={`inline-flex items-center justify-center gap-2 rounded-2xl px-4 py-3 font-semibold transition active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-70 ${className}`}
    >
      {isLoading ? (
        <>
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
          <span>Processing...</span>
        </>
      ) : (
        children
      )}
    </button>
  );
}
