import React, { useState, useEffect } from "react";
import {Source, Layer} from 'react-map-gl';
import triangleIcon from '../map-icons/diamond.svg'

 const IfcbLayer = ({mapRef}) => {
   const mapObj = mapRef.current.getMap();
   console.log(mapObj);
   const width = 24 ; // The image will be 64 pixels square
   const bytesPerPixel = 4; // Each pixel is represented by 4 bytes: red, green, blue, and alpha.
   const data = new Uint8ClampedArray(width * width * bytesPerPixel);

   // Iterate through every pixel
   for (let i = 0; i < data.length; i += 4) {
     data[i + 0] = 117;    // R value
     data[i + 1] = 107;  // G value
     data[i + 2] = 177;    // B value
     data[i + 3] = 220;  // A value
   }
   //mapObj.addImage('square', { width: width, height: width, data: data });

   useEffect(() => {
     const triangleImg = new Image(30,30);
     //triangleImg.onload = () => mapObj.addImage('triangle', triangleImg);
     triangleImg.src = triangleIcon;
    }, [])

   const ifcbSource = {
     id: 'ifcb-src',
     type: 'geojson',
     data: 'https://habhub.whoi.edu/ifcb-datasets/maps/ajax/load-all-datasets/',
     buffer: 0,
     maxzoom: 12,
   }

   const ifcbLayer = {
     id: 'ifcb-layer',
     type: 'circle',
     source: 'ifcb_src',
     paint: {
       'circle-color': 'lightblue',
       'circle-opacity': 0.8,
       'circle-radius': 12,
       'circle-stroke-color': 'darkblue',
       'circle-stroke-width': 2
     },
     layout: {
       'visibility': 'visible',
     },
   }

   return (
     <Source {...ifcbSource}>
       <Layer {...ifcbLayer} />
     </Source>
   )
}

export default IfcbLayer;
