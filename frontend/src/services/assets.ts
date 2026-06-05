import { apiClient } from "./client";
import type { AssetAlert, AssetHealth, AssetOverview, MlPrediction, Prediction } from "../types/assets";

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
