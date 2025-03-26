// fetchData.ts
import axios from "axios";
import { RootEndpointData } from "../interfaces/interfaces";

export const fetchData = async () => {
  try {
    const [rootResponse, emailsResponse] = await Promise.all([
      axios.get<RootEndpointData>("/api/landing"),
      axios.get<string[]>("/api/get_emails"),
    ]);

    if (rootResponse.status !== 200 || emailsResponse.status !== 200) {
      throw new Error(
        `HTTP error! Grants status: ${rootResponse.status}, Emails status: ${emailsResponse.status}`
      );
    }

    return { rootData: rootResponse.data, emails: emailsResponse.data }; // Return both
  } catch (error) {
    // Handle errors (e.g., re-throw or return specific error object)
    throw new Error("Error fetching data: " + error);
  }
};