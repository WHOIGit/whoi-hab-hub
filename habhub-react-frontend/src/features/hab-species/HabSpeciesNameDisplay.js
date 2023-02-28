import React from "react";

export default function HabSpeciesNameDisplay({ species }) {
  const syndrome = species.syndrome ? "/ " + species.syndrome : "";
  return (
    <span>
      <em>{species.displayName}</em> {syndrome}
    </span>
  );
}
