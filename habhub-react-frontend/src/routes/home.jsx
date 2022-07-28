import React, { useEffect } from "react";
import { sub } from "date-fns";
import { useDispatch } from "react-redux";
// Import our stuff
import MapContainer from "../app/MapContainer";
import { changeDateRange } from "../features/date-filter/dateFilterSlice";

// Get user set startDate from .env if available
let defaultStartDate;
if (
  process.env.REACT_APP_INITIAL_DATE_RANGE_YEARS &&
  process.env.REACT_APP_INITIAL_DATE_RANGE_MONTHS &&
  process.env.REACT_APP_INITIAL_DATE_RANGE_DAYS
) {
  defaultStartDate = sub(new Date(), {
    years: process.env.REACT_APP_INITIAL_DATE_RANGE_YEARS,
    months: process.env.REACT_APP_INITIAL_DATE_RANGE_MONTHS,
    days: process.env.REACT_APP_INITIAL_DATE_RANGE_DAYS,
  }).toISOString();
}

export default function Home() {
  let dispatch = useDispatch();
  console.log("HOME");
  useEffect(() => {
    if (defaultStartDate) {
      let payload = {
        startDate: defaultStartDate,
        endDate: new Date().toISOString(),
        seasonal: false,
        excludeMonthRange: false,
      };
      dispatch(changeDateRange(payload));
    }
  }, []);

  return <MapContainer />;
}
