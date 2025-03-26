import React from "react";
import "../styles/scrapingSpinner.css";

const LoadingSpinner: React.FC = () => (
  <div id="loading">
    <div className="spinner"></div>
    <p>Scraping in progress, please wait...</p>
  </div>
);

export default LoadingSpinner;
