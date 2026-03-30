export function JapanFlag({ className = "w-6 h-4" }: { className?: string }) {
  return (
    <svg viewBox="0 0 900 600" className={className}>
      <rect fill="#fff" height="600" width="900"/>
      <circle fill="#bc002d" cx="450" cy="300" r="180"/>
    </svg>
  );
}
