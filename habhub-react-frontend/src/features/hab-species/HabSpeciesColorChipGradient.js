import React from "react";

// default to show all colors in gradient list
// if chipType is "primary", only show single chip for primary color
export default function HabSpeciesColorChip({
  species,
  chipWidth = 20,
  chipHeight = 20,
  chipType = "gradient"
}) {
  let colors = species.colorGradient;

  if (chipType === "primary") {
    colors = [species.primaryColor];
  }

  if (!colors) {
    return null;
  }

  let svgWidth = chipWidth * colors.length;

  return (
    <svg width={svgWidth} height={chipHeight}>
      {colors.map((color, index) => (
        <rect
          width={chipWidth}
          height={chipHeight}
          fill={color}
          x={index * chipWidth}
          key={index}
        ></rect>
      ))}
    </svg>
  );
}
