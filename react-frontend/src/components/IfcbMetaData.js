import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import {
  Typography,
  Button,
  Grid,
  GridList,
  GridListTile,
  CircularProgress,
} from '@material-ui/core';

const API_URL = process.env.REACT_APP_API_URL

const useStyles = makeStyles((theme) => ({
  placeholder: {
    textAlign: 'center',
  },
  rootGrid: {
    marginTop: theme.spacing(2),
    display: 'flex',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
    backgroundColor: theme.palette.background.paper,
  },
  imageGrid: {
    maxWidth: '100%',
  },
  gridList: {
    flexWrap: 'nowrap',
    // Promote the list into his own layer on Chrome. This cost memory but helps keeping high FPS.
    transform: 'translateZ(0)',
  },
}));

const IfcbMetaData = ({metaDataUrl, chartExpanded}) => {
  const classes = useStyles();
  const [pointImgData, setPointImgData] = useState();
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);

  const gridSize = chartExpanded ? 3 : 6;

  useEffect(() => {
    console.log(metaDataUrl);
    fetch(metaDataUrl)
      .then(res => res.json())
      .then(
        (result) => {
          console.log(result);
          setIsLoaded(true);
          setPointImgData(result);
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
          setIsLoaded(true);
          setError(error);
        }
      )

  }, [metaDataUrl])

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
          <Grid container spacing={3} >
            <Grid item xs>
              <Typography variant="h6">
                <em>{pointImgData.species}</em>
              </Typography>
              <Typography variant="body2">
                IFCB Bin: {pointImgData.bin.pid}
              </Typography>
            </Grid>
            <Grid item xs style={{ textAlign:'right' }}>
              <Button
                size="small"
                color="primary"
                href={`https://ifcb-data.whoi.edu/bin?dataset=${ pointImgData.bin.dataset_id }&bin=${ pointImgData.bin.pid }`}
                target="_blank" >
                IFCB Dashboard source link
              </Button>
            </Grid>
          </Grid>
        </div>
        <div className={classes.rootGrid}>
          <Grid container spacing={2} >
            {pointImgData.images.map((image) => (
              <Grid item xs={gridSize}>
                <img
                  src={`${API_URL}/media/${image}`}
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
}

export default IfcbMetaData;
