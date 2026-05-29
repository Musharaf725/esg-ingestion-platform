export default function ErrorState({ message, onRetry }) {
  return (
    <div className="glass-panel border border-rose-400/30 bg-rose-500/10 p-4 text-sm text-rose-100">
      <p className="font-medium">{message || "Something went wrong."}</p>
      {onRetry ? (
        <button
          onClick={onRetry}
          className="mt-3 rounded-lg border border-rose-300/30 px-3 py-1.5 text-xs font-medium text-rose-50 transition hover:bg-rose-500/20"
        >
          Retry
        </button>
      ) : null}
    </div>
  );
}
