import React from "react";
import { Grant } from "../interfaces/interfaces";

interface ScrapeAgainButtonProps {
  grant: Grant;
  // onScrape is a function that accepts a Grant object as parameter and returns void.
  onScrape: (grant: Grant) => void;
}

const ScrapeAgainButton: React.FC<ScrapeAgainButtonProps> = ({
  grant,
  onScrape,
}) => {
  const handleClick = () => {
    onScrape(grant);
  };

  return (
    <button
      className="scrape-again-btn"
      onClick={handleClick}
      disabled={grant.status === "Invalid"}
    >
      Scrape Again
    </button>
  );
};

export default ScrapeAgainButton;
