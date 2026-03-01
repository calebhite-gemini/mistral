interface StatCardProps {
  label: string;
  value: string;
  icon: React.ReactNode;
  sentiment?: { label: string; progress: number };
  loading?: boolean;
}

function StatCard({ label, value, icon, sentiment, loading }: StatCardProps) {
  return (
    <div className="bg-[#18181b]/50 border border-[#27272a] rounded-sm p-4 flex-1 flex flex-col justify-between min-h-[112px]">
      <div className="flex items-start justify-between">
        <span className="text-[#64748b] text-xs font-medium tracking-[0.6px] uppercase">{label}</span>
        <span className="text-[#64748b]">{icon}</span>
      </div>
      <div className="flex flex-col gap-1">
        {loading ? (
          <span className="text-[#64748b] text-xl font-mono font-bold">--</span>
        ) : sentiment ? (
          <>
            <span className="text-white text-xl font-mono font-bold uppercase">{sentiment.label}</span>
            <div className="bg-[#27272a] h-1 rounded-none overflow-hidden">
              <div className="bg-[#10b981] h-full" style={{ width: `${sentiment.progress}%` }} />
            </div>
          </>
        ) : (
          <span className="text-white text-xl font-mono font-bold">{value}</span>
        )}
      </div>
    </div>
  );
}

interface StatsCardsProps {
  volume?: number;
  activeMarkets?: number;
  loading?: boolean;
}

function formatMoney(n: number): string {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `$${(n / 1_000).toFixed(1)}K`;
  return `$${n.toLocaleString()}`;
}

export default function StatsCards({ volume, activeMarkets, loading }: StatsCardsProps) {
  return (
    <div className="flex gap-4">
      <StatCard
        label="Volume"
        value={volume !== undefined ? formatMoney(volume) : "--"}
        loading={loading}
        icon={
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
          </svg>
        }
      />
      <StatCard
        label="Games Today"
        value={activeMarkets !== undefined ? activeMarkets.toLocaleString() : "--"}
        loading={loading}
        icon={
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" />
          </svg>
        }
      />
    </div>
  );
}
