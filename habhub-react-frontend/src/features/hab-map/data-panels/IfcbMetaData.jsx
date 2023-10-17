import React, { useState, useEffect } from "react";
import { makeStyles } from "@material-ui/core/styles";
import { Typography, Button, Grid, CircularProgress } from "@material-ui/core";

import axiosInstance from "../../../app/apiAxios";

const useStyles = makeStyles((theme) => ({
  placeholder: {
    textAlign: "center",
  },
  rootGrid: {
    marginTop: theme.spacing(2),
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "space-around",
    backgroundColor: theme.palette.background.paper,
  },
  imageGrid: {
    maxWidth: "100%",
  },
  gridList: {
    flexWrap: "nowrap",
    // Promote the list into his own layer on Chrome. This cost memory but helps keeping high FPS.
    transform: "translateZ(0)",
  },
}));

const IfcbMetaData = ({ metaDataUrl, chartExpanded }) => {
  const classes = useStyles();
  const [pointImgData, setPointImgData] = useState();
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [isLoaded, setIsLoaded] = useState(false);

  const gridSize = chartExpanded ? 3 : 6;

  useEffect(() => {
    console.log(metaDataUrl);
    async function fetchResults() {
      try {
        const res = await axiosInstance.get(metaDataUrl);
        console.log(res.request.responseURL);
        setIsLoaded(true);
        setPointImgData(res.data);
      } catch (error) {
        setIsLoaded(true);
        setError(error);
      }
    }
    fetchResults();
  }, [metaDataUrl]);

  return (
    <div>
      {!pointImgData && (
        <div className={classes.placeholder}>
          <CircularProgress />
        </div>
      )}

      {pointImgData && (
        <div>
          <div>
            <Grid container spacing={3}>
              <Grid item xs>
                <Typography variant="h6">
                  <em>{pointImgData.species}</em>
                </Typography>
                <Typography variant="body2">
                  IFCB Bin: {pointImgData.bin.pid}
                </Typography>
              </Grid>
              <Grid item xs style={{ textAlign: "right" }}>
                <Button
                  size="small"
                  color="primary"
                  href={`${pointImgData.bin.datasetLink}/bin?dataset=${pointImgData.bin.datasetId}&bin=${pointImgData.bin.pid}`}
                  target="_blank"
                >
                  IFCB Dashboard source link
                </Button>
              </Grid>
            </Grid>
          </div>
          <div className={classes.rootGrid}>
            <Grid container spacing={2}>
              {pointImgData.images.map((image) => (
                <Grid item xs={gridSize} key={image}>
                  <img
                    src={image}
                    alt={pointImgData.species}
                    className={classes.imageGrid}
                  />
                </Grid>
              ))}
            </Grid>
          </div>
        </div>
      )}
    </div>
  );
};

export default IfcbMetaData;
