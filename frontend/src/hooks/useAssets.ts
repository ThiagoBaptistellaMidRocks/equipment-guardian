import { useQuery } from "@tanstack/react-query";
import { getAsset, listAlerts, listAssets, listHealth } from "../services/assets";

export function useAssets() {
  return useQuery({
    queryKey: ["assets"],
    queryFn: listAssets
  });
}

export function useAsset(assetId: string | null) {
  return useQuery({
    queryKey: ["assets", assetId],
    queryFn: () => getAsset(assetId ?? ""),
    enabled: Boolean(assetId)
  });
}

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: listHealth
  });
}

export function useAlerts() {
  return useQuery({
    queryKey: ["alerts"],
    queryFn: listAlerts
  });
}
