import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useParams } from "react-router-dom";

// Import our stuff
import MapContainer from "../app/MapContainer";
import axiosInstance from "../app/apiAxios";
import { changeDateRange } from "../features/date-filter/dateFilterSlice";
import {
  setAllLayersVisibility,
  changeMaxMean,
} from "../features/data-layers/dataLayersSlice";
import { setAllSpeciesVisibility } from "../features/hab-species/habSpeciesSlice";
import { setAllFeatures } from "../features/hab-map/habMapDataSlice";

export default function Bookmark() {
  const params = useParams();
  const bookmarkId = params.bookmarkId;
  const dispatch = useDispatch();
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [isLoaded, setIsLoaded] = useState(false);
  const [viewport, setViewport] = useState(null);

  useEffect(() => {
    async function fetchBookmark() {
      try {
        const res = await axiosInstance.get(
          `api/v1/core/map-bookmarks/${bookmarkId}`
        );

        setIsLoaded(true);
        const bookmarkData = res.data;
        console.log(bookmarkData);

        const datePayload = {
          startDate: bookmarkData.startDate,
          endDate: bookmarkData.endDate,
          seasonal: bookmarkData.seasonal,
          excludeMonthRange: bookmarkData.excludeMonthRange,
        };
        // set Date Range
        dispatch(changeDateRange(datePayload));

        // set Data Layers
        const layerPayload = {
          layerList: bookmarkData.dataLayers,
        };
        dispatch(setAllLayersVisibility(layerPayload));

        // set visible Species
        const speciesPayload = {
          speciesList: bookmarkData.species,
        };
        dispatch(setAllSpeciesVisibility(speciesPayload));

        // set Max/Mean
        const maxMeanPayload = {
          value: bookmarkData.maxMean,
        };
        dispatch(changeMaxMean(maxMeanPayload));

        // set Active Features
        const featurePayload = bookmarkData.activeFeatures;
        dispatch(setAllFeatures(featurePayload));

        // set Map Viewport
        const viewport = {
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
