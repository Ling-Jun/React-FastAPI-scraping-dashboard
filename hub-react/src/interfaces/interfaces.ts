// interfaces.ts

// interfaces are similar to Python Abstract Classes
export interface Grant {
    page: string;
    date: string;
    status: string;
    diff: string;
  }
  
  export interface RootEndpointData {
    grants: Grant[];
    keywords: string;
    schedules: string;
  }

export interface RenderTableProps {
    emails: string[];
    rootData: RootEndpointData;
    onScrapeAgain: (grant: Grant)=>{};
    onStatusUpdate:(grant: Grant)=>void;
  }
  