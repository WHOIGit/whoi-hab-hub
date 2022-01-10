import React, { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { useDispatch } from "react-redux";
// Import our stuff
import MapContainer from "../app/MapContainer";
import { changeDateRange } from "../features/date-filter/dateFilterSlice";

function isIsoDate(str) {
  if (!/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z/.test(str)) return false;
  let d = new Date(str);
  return d.toISOString() === str;
}

export default function Bookmark() {
  let dispatch = useDispatch();
  // eslint-disable-next-line no-unused-vars
  let [bookmarkParams, setBookmarkParams] = useSearchParams();

  useEffect(() => {
    let seasonal = bookmarkParams.get("seasonal");
    let startDate = bookmarkParams.get("startDate");
    let endDate = bookmarkParams.get("endDate");
    let excludeMonthRange = bookmarkParams.get("excludeMonthRange");
    console.log(seasonal);
    console.log(endDate);

    if (isIsoDate(startDate) && isIsoDate(endDate)) {
      let payload = {
        startDate: startDate.toISOString(),
        endDate: endDate.toISOString(),
        seasonal: seasonal,
        excludeMonthRange: excludeMonthRange,
      };
      dispatch(changeDateRange(payload));
    }
  }, []);

  return <MapContainer />;
}
