import React, { useState, useEffect } from "react";
import {Source, Layer} from 'react-map-gl';
import { format } from 'date-fns';

const API_URL = process.env.REACT_APP_API_URL

export default function ClosuresLayer({mapRef, dateFilter}) {
   const mapObj = mapRef.current.getMap();
   console.log(mapObj);
   const [error, setError] = useState(null);
   const [isLoaded, setIsLoaded] = useState(false);
   const [results, setResults] = useState();
   const [apiURL, setApiURL] = useState();

   useEffect(() => {
     function getFetchUrl() {
       let baseURL = API_URL + 'api/v1/closures/'
       let filterURL = ''
       // build API URL to get set Date Filter
       if (dateFilter.length) {
         filterURL = baseURL + '?' + new URLSearchParams({
             start_date: format(dateFilter[0], 'MM/dd/yyyy'),
             end_date: format(dateFilter[1], 'MM/dd/yyyy'),
             state: 'MA',
         })
         //return filterURL;
       }
       //return baseURL;
       setApiURL(filterURL)
     }

     function fetchResults() {
       const url = getFetchUrl();
       console.log(url);
       fetch(url)
         .then(res => res.json())
         .then(
           (result) => {
             console.log(result);
             setIsLoaded(true);
             setResults(result);
           },
           // Note: it's important to handle errors here
           // instead of a catch() block so that we don't swallow
           // exceptions from actual bugs in components.
           (error) => {
             setIsLoaded(true);
             setError(error);
           }
         )
     }
     //fetchResults();
     getFetchUrl()
   }, [dateFilter])

  console.log(results);

  const source = {
   id: 'closures-src',
   type: 'geojson',
   data: apiURL,
   buffer: 0,
   maxzoom: 12,
  }

  const layer = {
   id: 'closures-layer',
   type: 'fill',
   source: 'closures',
   paint: {
     'fill-color': 'orange',
     'fill-opacity': 0.5,
     'fill-outline-color': '#fc4e2a',
   },
   layout: {
     'visibility': 'visible',
   },
  }

  return (
   <Source {...source}>
     <Layer {...layer} />
   </Source>
  )
}
