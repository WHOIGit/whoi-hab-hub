import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useParams } from "react-router-dom";

// Import our stuff
import MapContainer from "../app/MapContainer";
import axiosInstance from "../app/apiAxios";
import { changeDateRange } from "../features/date-filter/dateFilterSlice";
import { changeLayerVisibility } from "../features/data-layers/dataLayersSlice";

export default function Bookmark() {
  let params = useParams();
  let bookmarkId = params.bookmarkId;
  let dispatch = useDispatch();
  // eslint-disable-next-line no-unused-vars
  let [error, setError] = useState(null);
  // eslint-disable-next-line no-unused-vars
  let [isLoaded, setIsLoaded] = useState(false);

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
        bookmarkData.dataLayers.forEach((item) => {
          let layerPayload = {
            layerID: item,
            checked: true,
          };
          dispatch(changeLayerVisibility(layerPayload));
        });
      } catch (error) {
        console.log(error.response);
        setIsLoaded(true);
        setError(error);
      }
    }

    if (!bookmarkId) return null;
    fetchBookmark();
  }, [bookmarkId]);

  return <MapContainer />;
}
