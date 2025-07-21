import { useState, useEffect, useMemo, useRef } from "react";
import useFetchWithAuth from "../../hooks/useFetchWithAuth";
// import { fetchTailoredResumes } from "../../http";

import { AgGridReact } from 'ag-grid-react'; // React Data Grid Component
import type { CustomCellRendererProps } from 'ag-grid-react';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import type { ICellRendererParams, SizeColumnsToFitGridStrategy, SizeColumnsToFitProvidedWidthStrategy, SizeColumnsToContentStrategy} from 'ag-grid-community';
import fileDownloadIcon from "../../assets/images/download-file-icon.png";

ModuleRegistry.registerModules([AllCommunityModule]);

type TailoredResumeResponse = {
  id: string,
  name: string;
  company: string;
  role: string;
  job_posting: string;
  created_at: string; 
}

type RowData = {
  name: string;
  [key: string]: unknown;
}

type ColDefs = {
  field: string;
  [key: string]: unknown;
}


export default function TailoredResumeTable() {
  const fetchWithAuth = useFetchWithAuth();
  const prevTailoredResumeData = useRef<unknown[]>([]);

  const [rowData, setRowData] = useState<RowData[]>([
    { company: "Tesla", name: "Arvind_Chandra_Tesla_071825.pdf", role: "Full-Stack Engineer", job_posting:"https://www.google.com", created_at: "2025-07-18" },
    { company: "Ford", name: "Arvind_Chandra_Ford_062425.pdf", role: "Frontend Engineer", job_posting: "https://www.yahoo.com", created_at: "2025-06-24" },
    { company: "OpenAI", name: "Arvind_Chandra_OpenAI_062325.pdf", role: "Software Engineer", job_posting: "https://www.microsoft.com", created_at: "2025-06-23" },
  ]);

  const [colDefs, setColumnDefs] = useState([
    { "field": 'name' },
    { "field": 'company' },
    { "field": 'role' },
    { 
      "field": 'job_posting',
      "headerName": "Job",
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
    }), [],
  );

  useEffect(() => {
    const fetchTailoredResumeData= async () => {
      try {
        const response  = await fetchWithAuth("http://localhost:8000/tailor/users/2/tailored-resumes");
        const tailoredResumeData = await response.json();
  
        if (!response.ok) {
            throw new Error("Failed to fetch tailored resumes");
        }

        if (!Array.isArray(tailoredResumeData)) {
          throw new Error("Tailored resume response improperly formatted");
        }

        // using stringify for deep equality comparison
        if (JSON.stringify(tailoredResumeData) !== JSON.stringify(prevTailoredResumeData.current)) {  
          const formattedRows = formatTailoredResumesToAgGridRows({ tailoredResumeData, columnDefs: colDefs });
          
          // TODO switch from typecasting once we have landed on a final table format
          if (formattedRows) {
            setRowData(formattedRows as RowData[]);
            prevTailoredResumeData.current = tailoredResumeData;
          }
        }
      } catch (err) {
        console.error('Fetch error:', err);
      }
    };

    fetchTailoredResumeData();
  }, [colDefs]);
  

  return (
    <div className="form-field">
        <label>Tailored Resumes:</label>
        <div className="grid" style={{ height: 200 }}>
          <AgGridReact
              rowData={rowData}
              columnDefs={colDefs}
              autoSizeStrategy={autoSizeStrategy}
          />
        </div>
    </div>
  );
};

function formatTailoredResumesToAgGridRows({tailoredResumeData, columnDefs}: {tailoredResumeData: TailoredResumeResponse[], columnDefs: ColDefs[]} ) {
  // retrieve our "field" key from each column in our Ag-Grid column definitions (e.g. "field": "company")
  const columnLabels = columnDefs.map((column) => column.field);

  // maps the values in our responseData to Ag-Grid rows by checking 
  // if our responseData keyes are a valid field name in our array of Ag-Grid columns
  const formattedTailoredResumeRows = tailoredResumeData.map((resume) =>
    Object.fromEntries(
      columnLabels
        .filter(key => key in resume)
        .map(key => [key, resume[key as keyof TailoredResumeResponse] ])
    )
  );
  
  return formattedTailoredResumeRows
};


function jobPostingCellRenderer({ data }: CustomCellRendererProps){
  return (
    <a href={data.job_posting} target="_blank" rel="noopener noreferrer">
      Link
    </a>
  );
};

function downloadCellRenderer({ data }: ICellRendererParams){
  return (
    <button onClick={() => console.log('File Downloaded')}><img src={fileDownloadIcon} width={15} height={15} alt="Download" /></button>
  );
};
