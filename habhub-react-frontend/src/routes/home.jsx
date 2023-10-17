import React, { useEffect } from "react";
import { sub } from "date-fns";
import { useDispatch } from "react-redux";
// Import our stuff
import MapContainer from "../app/MapContainer";
import { changeDateRange } from "../features/date-filter/dateFilterSlice";

// Get user set startDate from .env if available
let defaultStartDate;
if (
  import.meta.env.VITE_INITIAL_DATE_RANGE_YEARS &&
  import.meta.env.VITE_INITIAL_DATE_RANGE_MONTHS &&
  import.meta.env.VITE_INITIAL_DATE_RANGE_DAYS
) {
  defaultStartDate = sub(new Date(), {
    years: import.meta.env.VITE_INITIAL_DATE_RANGE_YEARS,
    months: import.meta.env.VITE_INITIAL_DATE_RANGE_MONTHS,
    days: import.meta.env.VITE_INITIAL_DATE_RANGE_DAYS,
  }).toISOString();
}

export default function Home() {
  const dispatch = useDispatch();

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
