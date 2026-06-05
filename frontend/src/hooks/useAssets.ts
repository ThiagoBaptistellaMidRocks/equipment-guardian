import { useQuery } from "@tanstack/react-query";
import { getAsset, getPrediction, listAlerts, listAssets, listHealth, listPredictions } from "../services/assets";

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

export function usePredictions() {
  return useQuery({
    queryKey: ["predictions"],
    queryFn: listPredictions
  });
}

export function usePrediction(assetId: string | null) {
  return useQuery({
    queryKey: ["predictions", assetId],
    queryFn: () => getPrediction(assetId ?? ""),
    enabled: Boolean(assetId),
    retry: false
  });
}
