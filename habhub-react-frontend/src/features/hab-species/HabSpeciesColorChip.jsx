import React from "react";

// default to show all colors in gradient list
// if chipType is "primary", only show single chip for primary color
export default function HabSpeciesColorChip({
  species,
  chipWidth = 20,
  chipHeight = 20,
  chipType = "opacity",
}) {
  let color = species.primaryColor;
  let opacities = [0.2, 0.4, 0.6, 0.8, 1];
  if (chipType === "primary") {
    color = species.primaryColor;
    opacities = [1];
  }

  if (!color) {
    return null;
  }

  let svgWidth = chipWidth * opacities.length;

  return (
    <svg width={svgWidth} height={chipHeight}>
      {opacities.map((opacity, index) => (
        <rect
          width={chipWidth}
          height={chipHeight}
          fill={color}
          fillOpacity={opacity}
          x={index * chipWidth}
          key={index}
        ></rect>
      ))}
    </svg>
  );
}
