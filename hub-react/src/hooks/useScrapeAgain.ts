// useScrapeAgain.ts
import { RootEndpointData, Grant } from "../interfaces/interfaces";
import axios from "axios";

const useScrapeAgain = (
  // const [rootData, setRootData] = useState<RootEndpointData | null>(null);
  // setRootData is a updater function represented by React.Dispatch<React.SetStateAction<S>>, where S is state type
  setRootData: React.Dispatch<React.SetStateAction<RootEndpointData | null>>,
  setIsScraping: React.Dispatch<React.SetStateAction<boolean>> // Accept the setter
) => {
  const handleScrapeAgain = async (grant: Grant) => {
    setIsScraping(true); // Start loading spinner
    try {
      const response = await axios.post("/api/add_grant", {
          url: grant.page,
          date: "",
          status: "",
          recipient: "",
        });

      if (response.status===200) {
        const data =  response.data;
        // console.log("response.data", data);
        // Replace 'T' with a space in the date string
        if (data.date) {
          data.date = data.date.replace('T', ' ');
        }
        setRootData((prevData) =>
          prevData
            ? {
                ...prevData,
                grants: prevData.grants.map((g) =>
                  g.page === grant.page ? { ...g, ...data } : g
                ),
              }
            : prevData
        );
      } else {
        alert(`Failed to scrape URL: ${grant.page}. Please try again.`);
      }
    } catch (error) {
      console.error(`Error scraping URL: ${grant.page}`, error);
      alert(
        `An error occurred while scraping URL: ${grant.page}. Please try again.`
      );
    }
    finally{
      setIsScraping(false); 
    }
  };

  return { handleScrapeAgain };
};

export default useScrapeAgain;
