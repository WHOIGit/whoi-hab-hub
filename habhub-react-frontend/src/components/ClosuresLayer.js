import React, {useState, useEffect} from "react";
import {Source, Layer} from 'react-map-gl';
import {format} from 'date-fns';

const API_URL = process.env.REACT_APP_API_URL

export default function ClosuresLayer({mapRef, habSpecies, dateFilter, stateFilter, visibility}) {
  const mapObj = mapRef.current.getMap();
  console.log(mapObj);
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();
  const [labels, setLabels] = useState();

  // Get Closure data from API
  useEffect(() => {
    function getFetchUrl() {
      let baseURL = API_URL + 'api/v1/closures/'
      let filterURL = ''
      // build API URL to get set Date Filter
      if (dateFilter.length) {
        filterURL = baseURL + '?' + new URLSearchParams({
          start_date: format(dateFilter[0], 'MM/dd/yyyy'),
          end_date: format(dateFilter[1], 'MM/dd/yyyy')
        })
        if (stateFilter) {
          filterURL = filterURL + new URLSearchParams({
            state: stateFilter
          })
        }
        return filterURL;
      }
      return baseURL;
    }

    function fetchResults() {
      const url = getFetchUrl();
      console.log(url);
      fetch(url).then(res => res.json()).then((result) => {
        setIsLoaded(true);
        setResults(result);
      },
      // Note: it's important to handle errors here
      // instead of a catch() block so that we don't swallow
      // exceptions from actual bugs in components.
      (error) => {
        setIsLoaded(true);
        setError(error);
      })
    }
    // Get the API data
    fetchResults();
  }, [dateFilter])

  // Need to create a new data source/layer to put label on polygon centroid
  // update the Labels text layer when API results change
  useEffect(() => {
    if (results) {
      const centerPoints = results.features.map(item => {
        const point = {
          "type": "Feature",
          "properties": {
            "name": item.properties.name,
            "count": item.properties.closures.length
          },
          "geometry": item.properties.geom_center_point
        }
        return point;
      })

      const labelsGeojson = {
        "type": "FeatureCollection",
        "features": centerPoints
      };
      setLabels(labelsGeojson);
      console.log(labelsGeojson);
    }
  }, [results])

  // Set default layer styles
  const layerClosures = {
    id: 'closures-layer',
    type: 'fill',
    source: 'closures-src',
    paint: {
      'fill-color': 'orange',
      'fill-opacity': 0.5,
      'fill-outline-color': '#fc4e2a'
    },
    layout: {
      'visibility': 'visible'
    }
  }
  /*
  const layerLabels = {
    id: 'closures-labels-layer',
    type: 'symbol',
    source: 'closures-labels-src',
    layout: {
      'visibility': 'visible',
      'text-field': ['get', 'count'],
      'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
      'text-size': 12
    }

  const layerLabelCircles = {
    id: 'closures-labels-circles-layer',
    type: 'circle',
    source: 'closures-labels-src',
    paint: {
      'circle-color': '#fed976',
      'circle-radius': 8,
      'circle-stroke-width': 0,
      'circle-stroke-color': '#feb24c'
    },
    layout: {
      'visibility': 'visible'
    }
  }
  */
  const layerClosuresIcons = {
    id: 'closures-icons-layer',
    type: 'symbol',
    source: 'closures-labels-src',
    layout: {
      'icon-image': 'icon-shellfish-closure',
      'icon-allow-overlap': false,
      'visibility': 'visible'
    }
  }

  if (!results || !labels) {
    return null;
  } else {
    return (
      <React.Fragment>
        <Source
          id="closures-src"
          type="geojson"
          data={results}
          buffer={10}
          maxzoom={12}
        >
        {visibility && (
          <Layer {...layerClosures}/>
        )}
        </Source>

        <Source
          id="closures-labels-src"
          type="geojson"
          data={labels}
        >
        {visibility && (
          <Layer {...layerClosuresIcons}/>
        )}
        </Source>


      </React.Fragment>
    )
  }

}
