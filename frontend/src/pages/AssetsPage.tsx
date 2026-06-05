import { useMemo, useState } from "react";
import { SideNav, TopBar } from "../components/AppChrome";
import { AssetDrawer } from "../components/AssetDrawer";
import { DashboardFilters } from "../components/DashboardFilters";
import { FleetSummary } from "../components/FleetSummary";
import { OperationsMap } from "../components/OperationsMap";
import { OperationsKpis } from "../components/OperationsKpis";
import { useAsset, useAssets } from "../hooks/useAssets";

export function AssetsPage() {
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);
  const assetsQuery = useAssets();
  const selectedAssetQuery = useAsset(selectedAssetId);

  const selectedAsset = useMemo(() => {
    if (selectedAssetQuery.data) {
      return selectedAssetQuery.data;
    }

    return assetsQuery.data?.find(({ asset }) => asset.id === selectedAssetId) ?? null;
  }, [assetsQuery.data, selectedAssetId, selectedAssetQuery.data]);

  return (
    <div className={`dashboard-layout ${selectedAssetId ? "drawer-open" : ""}`}>
      <TopBar />
      <SideNav />
      <DashboardFilters selectedAssetId={selectedAssetId} />

      {assetsQuery.isLoading ? (
        <section className="panel-state">Loading assets...</section>
      ) : assetsQuery.isError ? (
        <section className="panel-state error">Unable to load assets from API.</section>
      ) : (
        <OperationsMap
          assets={assetsQuery.data ?? []}
          selectedAssetId={selectedAssetId}
          onAssetSelect={setSelectedAssetId}
        />
      )}

      {!selectedAssetId ? <OperationsKpis /> : null}
      <FleetSummary assets={assetsQuery.data ?? []} />

      <AssetDrawer
        assetOverview={selectedAsset}
        isLoading={selectedAssetQuery.isLoading}
        onClose={() => setSelectedAssetId(null)}
      />
    </div>
  );
}
