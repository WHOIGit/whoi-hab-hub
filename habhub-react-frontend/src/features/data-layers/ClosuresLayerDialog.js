import React from "react";
import { withStyles } from "@material-ui/core/styles";
import Dialog from "@material-ui/core/Dialog";
import { Link } from "@material-ui/core";
import MuiDialogTitle from "@material-ui/core/DialogTitle";
import MuiDialogContent from "@material-ui/core/DialogContent";
import IconButton from "@material-ui/core/IconButton";
import CloseIcon from "@material-ui/icons/Close";
import Typography from "@material-ui/core/Typography";

const styles = (theme) => ({
  root: {
    margin: 0,
    padding: theme.spacing(2),
  },
  closeButton: {
    position: "absolute",
    right: theme.spacing(1),
    top: theme.spacing(1),
    color: theme.palette.grey[500],
  },
});

const DialogTitle = withStyles(styles)((props) => {
  const { children, classes, onClose, ...other } = props;
  return (
    <MuiDialogTitle disableTypography className={classes.root} {...other}>
      <Typography variant="h6">{children}</Typography>
      {onClose ? (
        <IconButton
          aria-label="close"
          className={classes.closeButton}
          onClick={onClose}
        >
          <CloseIcon />
        </IconButton>
      ) : null}
    </MuiDialogTitle>
  );
});

const DialogContent = withStyles((theme) => ({
  root: {
    padding: theme.spacing(2),
  },
}))(MuiDialogContent);

export default function ClosuresLayerDialog() {
  const [open, setOpen] = React.useState(true);

  const handleClose = () => {
    setOpen(false);
  };

  return (
    <div>
      <Dialog
        onClose={handleClose}
        aria-labelledby="closures-warning"
        open={open}
      >
        <DialogTitle id="closures-warning" onClose={handleClose}>
          Shellfish Closure Data Notice
        </DialogTitle>
        <DialogContent dividers>
          <Typography gutterBottom>
            This instance of HABhub provides visualizations and links of past
            biotoxin-based closures only from waters of Maine, New Hampshire,
            and Massachusetts.{" "}
            <strong>
              It should not be used as a source of information about current
              closure status of harvest areas.
            </strong>
          </Typography>
          <Typography gutterBottom>
            For the most up-to-date information, see sites maintained by{" "}
            <Link
              href="https://www.maine.gov/dmr/fisheries/shellfish/closures"
              target="_blank"
              rel="noreferrer"
            >
              Maine Department of Marine Resources
            </Link>
            ,{" "}
            <Link
              href="https://www4.des.state.nh.us/CoastalAtlas/Atlas.html"
              target="_blank"
              rel="noreferrer"
            >
              New Hampshire Department of Environmental Services
            </Link>
            , and{" "}
            <Link
              href="https://www.mass.gov/lists/biotoxin-notices"
              target="_blank"
              rel="noreferrer"
            >
              Massachusetts Division of Marine Fisheries
            </Link>{" "}
            and seek guidance from local town managers before harvesting.
          </Typography>
        </DialogContent>
      </Dialog>
    </div>
  );
}
