import { sub, differenceInDays, parseISO } from "date-fns";
import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  startDate: sub(new Date(), { years: 3 }).toISOString(),
  endDate: new Date().toISOString(),
  seasonal: false,
  excludeMonthRange: false,
  smoothingFactor: 4,
};

function handleSmoothingFactor(startDate, endDate) {
  // calculate the date range length to determine a smoothing factor to pass API
  const dateRange = differenceInDays(parseISO(endDate), parseISO(startDate));
  let newFactor = 4;

  if (dateRange < 90) {
    newFactor = 1;
  } else if (dateRange < 180) {
    newFactor = 2;
  } else if (dateRange < 240) {
    newFactor = 3;
  }
  return newFactor;
}

export const dateFilterSlice = createSlice({
  name: "dateFilter",
  initialState: initialState,
  reducers: {
    changeDateRange: {
      reducer(state, action) {
        state.startDate = action.payload.startDate;
        state.endDate = action.payload.endDate;
        state.smoothingFactor = action.payload.smoothingFactor;
      },
      prepare(payload) {
        return {
          payload: {
            startDate: payload.startDate,
            endDate: payload.endDate,
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
export const { changeDateRange } = dateFilterSlice.actions;

export default dateFilterSlice.reducer;
