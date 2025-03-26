// useExpandedRows.ts
import { useState } from 'react';

const useExpandedRows = () => {
  // initializes the expandedRows state as an empty object. Each key in this object corresponds to a page, and its boolean value
  // indicates whether the row is expanded (true) or collapsed (false).
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});

  const toggleDiff = (url: string) => {
    setExpandedRows((prevState) => ({
      ...prevState,
      [url]: !prevState[url], // Toggle the expanded state for this row
    }));
  };
    // toggleDiff takes a page identifier as an argument and updates the expandedRows state:
    // It spreads the prevState to maintain existing row states, and toggles the boolean value for the specified page,
    // effectively expanding or collapsing the corresponding row.​
    // prevState is the previous state of expandedRows.
    // spreading prevState retains the existing expanded states of all rows,
    // toggling [url]: !prevState[url] updates the expanded state of the row identified by url.​
    // Key Points:
    // Functional Updates: Using a function inside setState ensures that you have the latest state value,
    // which is crucial when the new state depends on the previous state. ​
    // State Updater Function: The function passed to setState receives the previous state as its argument (prevState),
    // allowing to compute the new state.


  return { expandedRows, toggleDiff };
};


export default useExpandedRows;
