import { apiClient } from "./client";
import type {
  AssetAlert,
  AssetHealth,
  AssetHistory,
  AssetOverview,
  AssetTimeline,
  FleetAnalytics,
  MlPrediction,
  Prediction
} from "../types/assets";

export async function listAssets(): Promise<AssetOverview[]> {
  const response = await apiClient.get<AssetOverview[]>("/api/assets");
  return response.data;
}

export async function getAsset(assetId: string): Promise<AssetOverview> {
  const response = await apiClient.get<AssetOverview>(`/api/assets/${assetId}`);
  return response.data;
}

export async function listHealth(): Promise<AssetHealth[]> {
  const response = await apiClient.get<AssetHealth[]>("/api/health");
  return response.data;
}

export async function listAlerts(): Promise<AssetAlert[]> {
  const response = await apiClient.get<AssetAlert[]>("/api/alerts");
  return response.data;
}

export async function listPredictions(): Promise<Prediction[]> {
  const response = await apiClient.get<Prediction[]>("/api/predictions");
  return response.data;
}

export async function getPrediction(assetId: string): Promise<Prediction> {
  const response = await apiClient.get<Prediction>(`/api/predictions/${assetId}`);
  return response.data;
}

export async function listMlPredictions(): Promise<MlPrediction[]> {
  const response = await apiClient.get<MlPrediction[]>('/api/ml/predictions');
  return response.data;
}

export async function getMlPrediction(assetId: string): Promise<MlPrediction> {
  const response = await apiClient.get<MlPrediction>(`/api/ml/predictions/${assetId}`);
  return response.data;
}

export async function getAssetHistory(assetId: string): Promise<AssetHistory> {
  const response = await apiClient.get<AssetHistory>(`/api/assets/${assetId}/history`);
  return response.data;
}

export async function getAssetTimeline(assetId: string): Promise<AssetTimeline> {
  const response = await apiClient.get<AssetTimeline>(`/api/assets/${assetId}/timeline`);
  return response.data;
}

export async function getFleetAnalytics(): Promise<FleetAnalytics> {
  const response = await apiClient.get<FleetAnalytics>("/api/analytics/fleet");
  return response.data;
}
