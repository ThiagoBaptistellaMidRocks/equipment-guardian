import { useQuery } from "@tanstack/react-query";
import { getAsset, getMlPrediction, getPrediction, listAlerts, listAssets, listHealth, listMlPredictions, listPredictions } from "../services/assets";

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

export function useMlPredictions() {
  return useQuery({
    queryKey: ["ml-predictions"],
    queryFn: listMlPredictions
  });
}

export function useMlPrediction(assetId: string | null) {
  return useQuery({
    queryKey: ["ml-predictions", assetId],
    queryFn: () => getMlPrediction(assetId ?? ""),
    enabled: Boolean(assetId),
    retry: false
  });
}
