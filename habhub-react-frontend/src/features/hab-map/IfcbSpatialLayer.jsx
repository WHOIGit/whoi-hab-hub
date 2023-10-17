import React from "react";
import IfcbSpatialMarkers from "./IfcbSpatialMarkers";

export default function IfcbSpatialLayer({ onMarkerClick, gridSquares }) {
  return (
    <div>
      {gridSquares.map(item => (
        <IfcbSpatialMarkers
          onMarkerClick={onMarkerClick}
          gridSquare={item}
          key={item.id}
        />
      ))}
    </div>
  );
}
