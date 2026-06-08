import { useMemo } from "react";
import ReactMapGL, { Marker, NavigationControl, Popup, ScaleControl } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";
import { useMlPredictions, usePredictions } from "../hooks/useAssets";
import type { AssetOverview, MlPrediction, Prediction } from "../types/assets";
import { assetIcon, assetToGeo, healthTone, MINE_INITIAL_VIEW } from "../utils/assets";

const SATELLITE_STYLE = {
  version: 8 as const,
  sources: {
    satellite: {
      type: "raster" as const,
      tiles: [
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      ],
      tileSize: 256,
      attribution: "© Esri, DigitalGlobe, GeoEye, Earthstar Geographics, CNES/Airbus DS",
    },
  },
  layers: [{ id: "satellite", type: "raster" as const, source: "satellite" }],
};

interface OperationsMapProps {
  assets: AssetOverview[];
  selectedAssetId: string | null;
  onAssetSelect: (assetId: string) => void;
}

function AssetMarkers({ assets, selectedAssetId, onAssetSelect }: OperationsMapProps) {
  const predictionsQuery = usePredictions();
  const mlPredictionsQuery = useMlPredictions();

  const predictionByAsset = useMemo(() => {
    const index = new Map<string, Prediction>();
    (predictionsQuery.data ?? []).forEach((p) => index.set(p.assetId, p));
    return index;
  }, [predictionsQuery.data]);

  const mlPredictionByAsset = useMemo(() => {
    const index = new Map<string, MlPrediction>();
    (mlPredictionsQuery.data ?? []).forEach((p) => index.set(p.assetId, p));
    return index;
  }, [mlPredictionsQuery.data]);

  return (
    <>
      {assets.map(({ asset, health }) => {
        const { latitude, longitude } = assetToGeo(asset.position);
        const tone = healthTone(health.riskLevel);
        const isSelected = selectedAssetId === asset.id;
        const prediction = predictionByAsset.get(asset.id);
        const mlPrediction = mlPredictionByAsset.get(asset.id);
        const showPredictionBadge = prediction && (health.riskLevel === "HIGH" || health.riskLevel === "CRITICAL");
        const showMlBadge = mlPrediction && (health.riskLevel === "HIGH" || health.riskLevel === "CRITICAL");

        return (
          <Marker
            key={asset.id}
            latitude={latitude}
            longitude={longitude}
            anchor="bottom"
            style={{ zIndex: isSelected ? 10 : 1 }}
          >
            <button
              className={`map-marker-label ${tone} ${isSelected ? "selected" : ""}`}
              type="button"
              onClick={() => onAssetSelect(asset.id)}
            >
              <span className="marker-glyph">{assetIcon(asset.assetType)}</span>
              <small>{asset.id}</small>
              {showPredictionBadge ? (
                <em className="prediction-badge">{prediction.eventType.replace("_", " ")}</em>
              ) : null}
              {showMlBadge ? (
                <em className="ml-badge">ML {Math.round(mlPrediction.probability * 100)}%</em>
              ) : null}
            </button>
          </Marker>
        );
      })}
    </>
  );
}

function AlertCallout({ assets, selectedAssetId }: { assets: AssetOverview[]; selectedAssetId: string | null }) {
  if (selectedAssetId) return null;

  const criticalAsset = assets.find(({ health }) => health.riskLevel === "CRITICAL");
  if (!criticalAsset) return null;

  const { latitude, longitude } = assetToGeo(criticalAsset.asset.position);

  return (
    <Popup
      latitude={latitude}
      longitude={longitude}
      anchor="bottom"
      closeButton={false}
      offset={125}
      className="alert-popup-wrapper"
    >
      <div className="alert-callout">
        <strong>Tire Overheat</strong>
        <span>RL: 187C Critical</span>
        <small>{criticalAsset.asset.id} - Rear Left Interior</small>
        <b>Failure flag in 14 min</b>
      </div>
    </Popup>
  );
}

export function OperationsMap({ assets, selectedAssetId, onAssetSelect }: OperationsMapProps) {
  return (
    <section className="operations-map" aria-label="Operations map">
      <ReactMapGL
        initialViewState={MINE_INITIAL_VIEW}
        mapStyle={SATELLITE_STYLE}
        style={{ width: "100%", height: "100%" }}
        attributionControl={false}
      >
        <NavigationControl position="bottom-right" showCompass={false} />
        <ScaleControl position="bottom-right" unit="metric" />
        <AssetMarkers assets={assets} selectedAssetId={selectedAssetId} onAssetSelect={onAssetSelect} />
        <AlertCallout assets={assets} selectedAssetId={selectedAssetId} />
      </ReactMapGL>
    </section>
  );
}
