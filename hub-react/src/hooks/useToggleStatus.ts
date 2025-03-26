// useToggleStatus.ts
import { useCallback } from "react";
import axios from "axios";
import { Grant } from "../interfaces/interfaces";

interface UseToggleStatusResult {
  toggleStatus: (grant: Grant, onStatusUpdate: (updatedGrant: Grant) => void) => Promise<void>;
}

export const useToggleStatus = (): UseToggleStatusResult => {
  const toggleStatus = 
  // useCallback() isn't strictly needed, however, if the component that uses this hook re-renders frequently AND
  // passes this function to memoized child components, then useCallback would be beneficial for performance
  useCallback(async (grant: Grant, onStatusUpdate: (updatedGrant: Grant) => void) => {
    const newStatus = grant.status.includes("TRIVIAL CHANGE!")
      ? "SIGNIFICANT CHANGE!"
      : "TRIVIAL CHANGE!";

    // updates the backend
    try {
      const response = await axios.post("/api/toggle_status", {
        url: grant.page,
        date: grant.date,  // Include the date
        status: newStatus,
        recipient: "", // If needed
      });
      if (response.status !== 200) {
        throw new Error(`Failed to toggle status: ${response.status}`);
      }

      // Update the grant object
      grant.status = newStatus;
      // Callback to update the parent component
      onStatusUpdate(grant);

    } catch (error) {
      console.error("Error updating status:", error);
      alert("Failed to toggle status. Please try again.");
    }
  }, []);


  return { toggleStatus };
};