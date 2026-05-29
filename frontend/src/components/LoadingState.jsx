export default function LoadingState({ message = "Loading..." }) {
  return (
    <div className="glass-panel flex items-center gap-3 p-4 text-slate-200">
      <div className="h-4 w-4 animate-spin rounded-full border-2 border-ops-300 border-t-transparent" />
      <span className="text-sm">{message}</span>
    </div>
  );
}
