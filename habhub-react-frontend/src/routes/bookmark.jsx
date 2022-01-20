import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useParams } from "react-router-dom";

// Import our stuff
import MapContainer from "../app/MapContainer";
import axiosInstance from "../app/apiAxios";
import { changeDateRange } from "../features/date-filter/dateFilterSlice";
import { setAllLayersVisibility } from "../features/data-layers/dataLayersSlice";
import { setAllSpeciesVisibility } from "../features/hab-species/habSpeciesSlice";

export default function Bookmark() {
  let params = useParams();
  let bookmarkId = params.bookmarkId;
  let dispatch = useDispatch();
  // eslint-disable-next-line no-unused-vars
  let [error, setError] = useState(null);
  // eslint-disable-next-line no-unused-vars
  let [isLoaded, setIsLoaded] = useState(false);
  let [viewport, setViewport] = useState(null);

  useEffect(() => {
    async function fetchBookmark() {
      try {
        let res = await axiosInstance.get(
          `api/v1/core/map-bookmarks/${bookmarkId}`
        );

        setIsLoaded(true);
        let bookmarkData = res.data;
        console.log(bookmarkData);

        let datePayload = {
          startDate: bookmarkData.startDate,
          endDate: bookmarkData.endDate,
          seasonal: bookmarkData.seasonal,
          excludeMonthRange: bookmarkData.excludeMonthRange,
        };
        // set Date Range
        dispatch(changeDateRange(datePayload));

        // set Data Layers
        let layerPayload = {
          layerList: bookmarkData.dataLayers,
        };
        dispatch(setAllLayersVisibility(layerPayload));

        // set visible Species
        let speciesPayload = {
          speciesList: bookmarkData.species,
        };
        dispatch(setAllSpeciesVisibility(speciesPayload));

        // set Map Viewport
        let viewport = {
          latitude: parseFloat(bookmarkData.latitude),
          longitude: parseFloat(bookmarkData.longitude),
          zoom: parseFloat(bookmarkData.zoom),
          width: "100%",
          height: "100vh",
        };
        setViewport(viewport);
      } catch (error) {
        console.log(error.response);
        setIsLoaded(true);
        setError(error);
      }
    }

    if (!bookmarkId) return null;
    fetchBookmark();
  }, [bookmarkId]);

  if (!viewport) return null;

  return <MapContainer bookmarkViewport={viewport} />;
}
