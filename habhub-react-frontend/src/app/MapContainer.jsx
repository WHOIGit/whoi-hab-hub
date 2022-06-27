import React, { useEffect, useState, useCallback } from "react";
import update from 'immutability-helper'
import { useDrop } from 'react-dnd'
import { useSelector } from "react-redux";
// Import our stuff
import HabMap from "../features/hab-map/HabMap";
import DashBoard from "../features/dashboard/DashBoard";
import DateControls from "../features/date-filter/DateControls";
//import LowerLeftPanel from "../features/legends/LowerLeftPanel";
import LegendPane from "../features/legends/LegendPane";
import { selectLayerLegendIds } from "../features/data-layers/dataLayersSlice";
import { ITEM_TYPES } from "../Constants";

const MAP_LATITUDE = parseFloat(process.env.REACT_APP_MAP_LATITUDE);
const MAP_LONGITUDE = parseFloat(process.env.REACT_APP_MAP_LONGITUDE);
const MAP_ZOOM = parseFloat(process.env.REACT_APP_MAP_ZOOM);

const defaultViewport = {
  latitude: MAP_LATITUDE,
  longitude: MAP_LONGITUDE,
  zoom: MAP_ZOOM,
  width: "100%",
  height: "100vh",
};
export default function MapContainer({ bookmarkViewport }) {
  const legendLayerIds = useSelector(selectLayerLegendIds);
  const [showControls, setShowControls] = useState(true);
  const [showDateControls, setShowDateControls] = useState(false);
  const [viewport, setViewport] = useState(defaultViewport);
  const [panes, setPanes] = useState({})
  console.log(panes);

  useEffect(() => {
    if (legendLayerIds) {
      const newPaneList = {};
      let bottom = 0;
      legendLayerIds.forEach(item => {
        newPaneList[item] = { bottom: bottom, left: 0 }
        bottom = bottom + 200;
      })
      setPanes(newPaneList)
    }
  }, [legendLayerIds]);

  useEffect(() => {
    if (bookmarkViewport) {
      setViewport(bookmarkViewport);
    }
  }, [bookmarkViewport]);

  const moveBox = useCallback(
    (dataLayer, left, bottom) => {
      console.log(dataLayer);
      setPanes(
        update(panes, {
          [dataLayer]: {
            $merge: { left, bottom },
          },
        }),
      )
    },
    [panes, setPanes],
  )

  const [, drop] = useDrop(
    () => ({
      accept: ITEM_TYPES.PANE,
      drop(item, monitor) {
        console.log(item);
        const delta = monitor.getDifferenceFromInitialOffset();
        const left = Math.round(item.left + delta.x);
        const bottom = Math.round(item.bottom - delta.y);
        moveBox(item.dataLayer, left, bottom);
        return undefined;
      },
    }),
    [moveBox]
  );

  return (
    <div ref={drop}>
     
        <HabMap viewport={viewport} setViewport={setViewport} />

        <DashBoard
          showControls={showControls}
          setShowControls={setShowControls}
          viewport={viewport}
        />

        <DateControls
          showControls={showControls}
          showDateControls={showDateControls}
          setShowDateControls={setShowDateControls}
        />

      {Object.keys(panes).map((key) => {
        const { left, bottom } = panes[key]
        return (
          <LegendPane
            key={key}
            dataLayer={key}
            id={key}
            left={left}
            bottom={bottom}
          />
            
        )
      })}
      
    </div>
  );
}
