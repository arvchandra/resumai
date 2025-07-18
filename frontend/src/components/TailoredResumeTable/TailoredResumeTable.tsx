import { useState, useMemo } from "react";
import useFetch from "../../hooks/useFetch";
import { fetchTailoredResumes } from "../../http";

import { AgGridReact } from 'ag-grid-react'; // React Data Grid Component
import type { CustomCellRendererProps } from 'ag-grid-react';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import type { ICellRendererParams, SizeColumnsToFitGridStrategy, SizeColumnsToFitProvidedWidthStrategy, SizeColumnsToContentStrategy} from 'ag-grid-community';
import fileDownloadIcon from "../../assets/images/download-file-icon.png";

ModuleRegistry.registerModules([AllCommunityModule]);

interface TailoredResume {
  name: string;
  company: string;
  role: string;
  job: string;
  created_at: string; 
  download: string;
}


export default function TailoredResumeTable() {
  const { fetchedData: tailoredResumes, isFetching, error } = useFetch(fetchTailoredResumes);

  const [rowData, setRowData] = useState([
    { company: "Tesla", name: "Arvind_Chandra_Tesla_071825.pdf", role: "Full-Stack Engineer", job:"https://www.google.com", created_at: "2025-07-18", download: "https://www.tesla.com" },
    { company: "Ford", name: "Arvind_Chandra_Ford_062425.pdf", role: "Frontend Engineer", job: "https://www.yahoo.com", created_at: "2025-06-24", download: "https://www.ford.com" },
    { company: "OpenAI", name: "Arvind_Chandra_OpenAI_062325.pdf", role: "Software Engineer", job: "https://www.microsoft.com", created_at: "2025-06-23", download: "https://www.toyota.com" },
  ]);

  const [colDefs, setColumnDefs] = useState([
    { "field": 'name' },
    { "field": 'company' },
    { "field": 'role' },
    { 
      "field": 'job',
      "cellRenderer": jobPostingCellRenderer,
    },
    { "field": 'created_at'  },
    { 
      "field": 'download' ,
      "cellRenderer": downloadCellRenderer,
    },
  ]);

  const autoSizeStrategy = useMemo<
    | SizeColumnsToFitGridStrategy 
    | SizeColumnsToFitProvidedWidthStrategy
    | SizeColumnsToContentStrategy
    >(() => ({
      type: "fitCellContents",
      defaultMaxWidth: 120,
    }),
    [],
  );


  

  return (
    <div className="form-field">
        <label>Select a resume:</label>
        <div className="grid" style={{ height: 200 }}>
        <AgGridReact
            rowData={rowData}
            columnDefs={colDefs}
            autoSizeStrategy={autoSizeStrategy}
            loading={isFetching}
        />
    </div>

    </div>
  );
};

function jobPostingCellRenderer({ data }: CustomCellRendererProps){
  return (
    <a href={data.job} target="_blank" rel="noopener noreferrer">
      Link
    </a>
  );
};

function downloadCellRenderer({ data }: ICellRendererParams){
  return (
    <button onClick={() => console.log('File Downloaded')}><img src={fileDownloadIcon} width={15} height={15} alt="Download" /></button>
  );
};