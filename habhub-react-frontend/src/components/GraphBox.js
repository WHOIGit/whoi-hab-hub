import React, { useState, useEffect } from "react";

const GraphBox = props =>  {
  const stationID = props.id;
  //const [stationID, setstationID] = useState(props.stationID);
  //const [feature, setFeature] = useState(props);
  console.log(stationID);

  return (
    <div className="graph-box">
    <h2>{stationID}</h2>

    </div>
  );
}

export default GraphBox;
