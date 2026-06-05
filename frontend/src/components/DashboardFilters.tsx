import { ChevronDown, Search } from "lucide-react";

export function DashboardFilters({ selectedAssetId }: { selectedAssetId: string | null }) {
  return (
    <div className="dashboard-filters">
      {selectedAssetId ? <button className="zoom-pill" type="button">2x Zoom</button> : null}
      <label className="search-control">
        <Search size={18} />
        <input aria-label="Search assets" placeholder={selectedAssetId ? "Search assets..." : "Search assets, roads..."} />
      </label>
      <button className="filter-pill" type="button">All Assets <ChevronDown size={14} /></button>
      <button className="filter-pill" type="button">All Status <ChevronDown size={14} /></button>
      <button className="filter-pill" type="button">Layers <ChevronDown size={14} /></button>
    </div>
  );
}
