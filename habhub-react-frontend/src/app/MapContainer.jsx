import React, { useEffect, useState, useCallback } from "react";
import update from 'immutability-helper'
import { useDrop } from 'react-dnd'
import { useSelector, useDispatch } from "react-redux";
// Import our stuff
import HabMap from "../features/hab-map/HabMap";
import DashBoard from "../features/dashboard/DashBoard";
import DateControls from "../features/date-filter/DateControls";
//import LowerLeftPanel from "../features/legends/LowerLeftPanel";
import LegendPane from "../features/legends/LegendPane";
import { selectLayerLegendIds } from "../features/data-layers/dataLayersSlice";
import { resetGuideSteps } from "../features/guide/guideSlice";
import GuidePane from "../features/guide/GuidePane";
import { ITEM_TYPES } from "../Constants";

export default function MapContainer({ bookmarkViewport }) {
  console.log("HABMAP");
  const dispatch = useDispatch();
  const legendLayerIds = useSelector(selectLayerLegendIds);
  const [showControls, setShowControls] = useState(true);
  const [showDateControls, setShowDateControls] = useState(false);
  const [guide, setGuide] = useState({guide: { bottom: "50%", left: "50%", transform: "translate(-50%, 50%)"}})
  const [panes, setPanes] = useState({})
  const [openGuide, setOpenGuide] = React.useState(false);

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

  const handleGuideClose = () => {
    setOpenGuide(false);
    // dispatch resetting all Guide Steps to inactive in Redux state
    dispatch(resetGuideSteps());
  };

  const movePane = useCallback(
    (id, left, bottom) => {
      console.log(id);
      setPanes(
        update(panes, {
          [id]: {
            $merge: { left, bottom },
          },
        }),
      )
    },
    [panes, setPanes],
  )

  const moveGuide = useCallback(
    (id, left, bottom, transform) => {
      console.log(id);
      setGuide(
        update(guide, {
          [id]: {
            $merge: { left, bottom, transform },
          },
        }),
      )
    },
    [guide, setGuide],
  )

  const [, drop] = useDrop(
    () => ({
      accept: ITEM_TYPES.PANE,
      drop(item, monitor) {
        console.log(item);
        let left, bottom
        const delta = monitor.getDifferenceFromInitialOffset();
        const offset = monitor.getInitialClientOffset();

        // need to check it the current item's left/bottom are in %
        if (isNaN(item.left) || isNaN(item.bottom)) { 
          // use the client offset function from DnD instead of left/bottom CSS
          // offset returns the middle x coordinate of the item, so need to correct by half width of guide
          left = Math.round(offset.x - 320 + delta.x);
          bottom = Math.round(offset.y - delta.y);
        } else {
          left = Math.round(item.left + delta.x);
          bottom = Math.round(item.bottom - delta.y);
        }
        
        console.log("OFFSET", offset);

        if (item.id === "guide") {
          moveGuide(item.id, left, bottom, "none");
        } else {
          movePane(item.id, left, bottom);
        }
        return undefined;
      },
    }),
    [movePane]
  );

  return (
    <div ref={drop}>
     
      <HabMap bookmarkViewport={bookmarkViewport} />

      <DashBoard
        showControls={showControls}
        setShowControls={setShowControls}
        setOpenGuide={setOpenGuide}
      />

      <DateControls
        showControls={showControls}
        showDateControls={showDateControls}
        setShowDateControls={setShowDateControls}
      />

      <GuidePane 
        openGuide={openGuide} 
        handleGuideClose={handleGuideClose} 
        left={guide["guide"].left}
        bottom={guide["guide"].bottom}
        transform={guide["guide"].transform}
        id={Object.keys(guide)[0]} 
      />

      {Object.keys(panes).map((key) => {
          const { left, bottom } = panes[key]
          return (
            <LegendPane
              key={key}
              dataLayer={key}
              left={left}
              bottom={bottom}
              id={key}
            />
          )
      })}
      
    </div>
  );
}
