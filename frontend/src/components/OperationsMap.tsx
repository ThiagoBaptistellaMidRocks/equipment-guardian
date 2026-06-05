import { Canvas, ThreeEvent } from "@react-three/fiber";
import { useLayoutEffect, useMemo, useRef } from "react";
import { Color, InstancedMesh, Matrix4, Vector3 } from "three";
import { useMlPredictions, usePredictions } from "../hooks/useAssets";
import type { AssetOverview, MlPrediction, Prediction } from "../types/assets";
import { assetIcon, healthTone, mapPositionToPercent } from "../utils/assets";

interface OperationsMapProps {
  assets: AssetOverview[];
  selectedAssetId: string | null;
  onAssetSelect: (assetId: string) => void;
}

const markerColors = {
  normal: "#10c991",
  warning: "#ffb000",
  critical: "#ff4a4f",
  offline: "#7c879a"
};

function MineTerrain() {
  const rings = [19, 28, 37, 46, 55];
  const gridLines = Array.from({ length: 21 }, (_, index) => (index - 10) * 8);

  return (
    <group>
      <mesh position={[0, -0.08, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[170, 110]} />
        <meshBasicMaterial color="#0b111e" />
      </mesh>
      {gridLines.map((line) => (
        <group key={line} rotation={[0, 0, -0.28]}>
          <mesh position={[line, 0, 0]}>
            <boxGeometry args={[0.06, 0.04, 140]} />
            <meshBasicMaterial color="#132033" transparent opacity={0.45} />
          </mesh>
          <mesh position={[0, 0.01, line]}>
            <boxGeometry args={[170, 0.04, 0.06]} />
            <meshBasicMaterial color="#132033" transparent opacity={0.35} />
          </mesh>
        </group>
      ))}
      <mesh position={[8, 0.02, -2]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[45, 96]} />
        <meshBasicMaterial color="#202c3c" transparent opacity={0.92} />
      </mesh>
      {rings.map((ring) => (
        <mesh key={ring} position={[8, 0.035, -2]} rotation={[-Math.PI / 2, 0, 0]} scale={[1.45, 0.66, 1]}>
          <ringGeometry args={[ring, ring + 0.25, 128]} />
          <meshBasicMaterial color="#33435a" transparent opacity={0.72} />
        </mesh>
      ))}
      <mesh position={[-2, 0.08, 0]} rotation={[0, -0.55, 0]}>
        <boxGeometry args={[74, 0.7, 2.1]} />
        <meshBasicMaterial color="#475365" transparent opacity={0.86} />
      </mesh>
      <mesh position={[-28, 0.09, -24]} rotation={[0, 1.1, 0]}>
        <boxGeometry args={[76, 0.72, 2.2]} />
        <meshBasicMaterial color="#536075" transparent opacity={0.82} />
      </mesh>
    </group>
  );
}

function AssetMarkerLayer({
  assets,
  selectedAssetId,
  onAssetSelect
}: OperationsMapProps) {
  const meshRef = useRef<InstancedMesh>(null);
  const matrix = useMemo(() => new Matrix4(), []);
  const color = useMemo(() => new Color(), []);

  useLayoutEffect(() => {
    const mesh = meshRef.current;
    if (!mesh) {
      return;
    }

    assets.forEach(({ asset, health }, index) => {
      const isSelected = selectedAssetId === asset.id;
      const scale = isSelected ? 2.15 : 1.45;
      matrix.compose(
        new Vector3(asset.position.x, 1.2, asset.position.y),
        mesh.quaternion,
        new Vector3(scale, 0.28, scale)
      );
      mesh.setMatrixAt(index, matrix);
      mesh.setColorAt(index, color.set(markerColors[healthTone(health.riskLevel)]));
    });

    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) {
      mesh.instanceColor.needsUpdate = true;
    }
  }, [assets, color, matrix, selectedAssetId]);

  function handleClick(event: ThreeEvent<MouseEvent>) {
    event.stopPropagation();
    if (typeof event.instanceId === "number") {
      onAssetSelect(assets[event.instanceId].asset.id);
    }
  }

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, assets.length]} onClick={handleClick}>
      <cylinderGeometry args={[1, 1, 1, 32]} />
      <meshBasicMaterial />
    </instancedMesh>
  );
}

function AssetLabels({
  assets,
  selectedAssetId,
  onAssetSelect
}: OperationsMapProps) {
  const predictionsQuery = usePredictions();
  const mlPredictionsQuery = useMlPredictions();
  const predictionByAsset = useMemo(() => {
    const index = new Map<string, Prediction>();
    (predictionsQuery.data ?? []).forEach((prediction) => {
      index.set(prediction.assetId, prediction);
    });
    return index;
  }, [predictionsQuery.data]);
  const mlPredictionByAsset = useMemo(() => {
    const index = new Map<string, MlPrediction>();
    (mlPredictionsQuery.data ?? []).forEach((prediction) => {
      index.set(prediction.assetId, prediction);
    });
    return index;
  }, [mlPredictionsQuery.data]);

  const visibleLabels = useMemo(() => {
    if (assets.length <= 120) {
      return assets;
    }

    return assets
      .filter(({ asset, health }) => asset.id === selectedAssetId || health.riskLevel !== "LOW")
      .slice(0, 80);
  }, [assets, selectedAssetId]);

  return (
    <div className="map-label-layer" aria-hidden="true">
      {visibleLabels.map(({ asset, health }) => {
        const position = mapPositionToPercent(asset.position);
        const tone = healthTone(health.riskLevel);
        const prediction = predictionByAsset.get(asset.id);
        const mlPrediction = mlPredictionByAsset.get(asset.id);
        const showPredictionBadge = prediction && (health.riskLevel === "HIGH" || health.riskLevel === "CRITICAL");
        const showMlBadge = mlPrediction && (health.riskLevel === "HIGH" || health.riskLevel === "CRITICAL");
        return (
          <button
            className={`map-marker-label ${tone} ${selectedAssetId === asset.id ? "selected" : ""}`}
            key={asset.id}
            style={{ left: `${position.left}%`, top: `${position.top}%` }}
            type="button"
            onClick={() => onAssetSelect(asset.id)}
          >
            <span className="marker-glyph">{assetIcon(asset.assetType)}</span>
            <small>{asset.id}</small>
            {showPredictionBadge ? <em className="prediction-badge">{prediction.eventType.replace("_", " ")}</em> : null}
            {showMlBadge ? <em className="ml-badge">ML {Math.round((mlPrediction.probability * 100))}%</em> : null}
          </button>
        );
      })}
    </div>
  );
}

function AlertCallout({ assets, selectedAssetId }: { assets: AssetOverview[]; selectedAssetId: string | null }) {
  if (selectedAssetId) {
    return null;
  }

  const criticalAsset = assets.find(({ health }) => health.riskLevel === "CRITICAL");
  if (!criticalAsset) {
    return null;
  }

  const position = mapPositionToPercent(criticalAsset.asset.position);

  return (
    <div className="alert-callout" style={{ left: `${Math.min(position.left + 8, 74)}%`, top: `${Math.max(position.top - 15, 10)}%` }}>
      <strong>Tire Overheat</strong>
      <span>RL: 187C Critical</span>
      <small>{criticalAsset.asset.id} - Rear Left Interior</small>
      <b>Failure flag in 14 min</b>
    </div>
  );
}

export function OperationsMap({ assets, selectedAssetId, onAssetSelect }: OperationsMapProps) {
  return (
    <section className="operations-map" aria-label="Operations map">
      <div className="map-canvas">
        <Canvas orthographic camera={{ position: [0, 90, 0], zoom: 7.5, near: 0.1, far: 200 }}>
          <ambientLight intensity={1} />
          <MineTerrain />
          <AssetMarkerLayer assets={assets} selectedAssetId={selectedAssetId} onAssetSelect={onAssetSelect} />
        </Canvas>
      </div>
      <AssetLabels assets={assets} selectedAssetId={selectedAssetId} onAssetSelect={onAssetSelect} />
      <AlertCallout assets={assets} selectedAssetId={selectedAssetId} />
      <div className="map-zoom">
        <button type="button">+</button>
        <button type="button">-</button>
      </div>
      <div className="map-scale"><span />0 - 250m</div>
    </section>
  );
}
