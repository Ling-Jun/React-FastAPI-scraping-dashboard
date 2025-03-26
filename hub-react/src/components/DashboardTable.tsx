// DashboardTable.tsx
import React, { useState, useEffect } from "react";
import { fetchData } from "../services/fetchData";
import { RootEndpointData } from "../interfaces/interfaces";
import RenderTable from "./RenderTable";
import useScrapeAgain from "../hooks/useScrapeAgain";
import LoadingSpinner from "./ScrapingSpinner";
import { Grant } from "../interfaces/interfaces";

const DashboardTable: React.FC = () => {
  const [rootData, setRootData] = useState<RootEndpointData | null>(null);
  const [emails, setEmails] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isScraping, setIsScraping] = useState(false);
  const { handleScrapeAgain } = useScrapeAgain(setRootData, setIsScraping);
  // useEffect(() => {
  //   if (isScraping) {
  //     console.log("LOADING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
  //   }
  // }, [isScraping]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const { rootData, emails } = await fetchData(); // Destructure response
        // updates rootData
        setRootData((prevRootData) =>
          prevRootData !== rootData ? { ...rootData } : prevRootData
        );
        // updates emails
        setEmails((prevEmails) =>
          prevEmails !== emails ? [...emails] : prevEmails
        );
      } catch (error) {
        setError("Error fetching data: " + error);
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const handleStatusUpdate = (updatedGrant: Grant) => {
    setRootData((prevRootData) => {
      if (!prevRootData) return prevRootData;

      const updatedGrants = prevRootData.grants.map((grant) =>
        // spreading updatedGrant into a new object ({ ...updatedGrant }), create a new Grant object with the updated status.
        // This object reference change triggers React to re-render
        grant.page === updatedGrant.page ? { ...updatedGrant } : grant
      );

      return { ...prevRootData, grants: updatedGrants }; // Also crucial for nested state updates
    });
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!rootData) return <div>No data available.</div>;

  return (
    <div>
      {isScraping ? <LoadingSpinner /> : ""}
      <RenderTable
        emails={emails}
        rootData={rootData}
        onScrapeAgain={handleScrapeAgain}
        onStatusUpdate={handleStatusUpdate}
      />
    </div>
  );
};

export default DashboardTable;
