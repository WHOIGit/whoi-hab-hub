import { sub, differenceInDays, parseISO } from "date-fns";
import { createSlice } from "@reduxjs/toolkit";
import { createSelector } from "reselect";

// Set small initial start date to avoid async data loading confusion
let initialStartDate = sub(new Date(), {
  years: 0,
  months: 0,
  days: 1,
}).toISOString();

// Get user set startDate from .env, set default if unavailable
let defaultStartDate = sub(new Date(), {
  years: 1,
  months: 0,
  days: 0,
}).toISOString();

// Get user set startDate from .env if available
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

const initialState = {
  defaultStartDate: defaultStartDate,
  startDate: initialStartDate,
  endDate: new Date().toISOString(),
  seasonal: false,
  excludeMonthRange: false,
  smoothingFactor: 8,
};

function handleSmoothingFactor(startDate, endDate) {
  // calculate the date range length to determine a smoothing factor to pass API
  const dateRange = differenceInDays(parseISO(endDate), parseISO(startDate));
  let newFactor = 8;

  if (dateRange < 180) {
    newFactor = 1;
  } else if (dateRange < 240) {
    newFactor = 3;
  }
  return newFactor;
}

export const dateFilterSlice = createSlice({
  name: "dateFilter",
  initialState: initialState,
  reducers: {
    changeDefaultStartDate: (state, action) => {
      state.defaultStartDate = action.payload.startDate;
    },
    changeDateRange: {
      reducer(state, action) {
        state.startDate = action.payload.startDate;
        state.endDate = action.payload.endDate;
        state.seasonal = action.payload.seasonal;
        state.excludeMonthRange = action.payload.excludeMonthRange;
        state.smoothingFactor = action.payload.smoothingFactor;
      },
      prepare(payload) {
        return {
          payload: {
            startDate: payload.startDate,
            endDate: payload.endDate,
            seasonal: payload.seasonal,
            excludeMonthRange: payload.excludeMonthRange,
            smoothingFactor: handleSmoothingFactor(
              payload.startDate,
              payload.endDate
            ),
          },
        };
      },
    },
  },
});

// Action creators are generated for each case reducer function
export const { changeDateRange, changeDefaultStartDate } =
  dateFilterSlice.actions;

export default dateFilterSlice.reducer;

// Selector functions
// use createSelector to create memoized selector
export const selectDateFilter = createSelector(
  (state) => state.dateFilter,
  (item) => item
);
