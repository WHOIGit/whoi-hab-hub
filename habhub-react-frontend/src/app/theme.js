import { createTheme, adaptV4Theme } from "@mui/material/styles";
import { orange } from '@mui/material/colors';

const theme = createTheme(adaptV4Theme({
  palette: {
    primary: { main: "#467fcf" },
    secondary: orange,
  },
}))
export default theme;
