import { useState, useEffect, useMemo } from "react";

import { AgGridReact } from 'ag-grid-react'; // React Data Grid Component
import type { CustomCellRendererProps } from 'ag-grid-react';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import DownloadCellRenderer from './DownloadCellRenderer.tsx';
import type {
  SizeColumnsToFitGridStrategy,
  SizeColumnsToFitProvidedWidthStrategy,
  SizeColumnsToContentStrategy
} from 'ag-grid-community';

import { useResumeApi } from "../../api/resumeApi.ts";

ModuleRegistry.registerModules([AllCommunityModule]);

type RowData = {
  name: string;
  [key: string]: unknown;
}

type ColDef = {
  field: string;
  [key: string]: unknown;
}

const colDefs: ColDef[] = [
  { "field": 'name' },
  { "field": 'company' },
  { "field": 'role' },
  {
    "field": 'job_posting',
    "headerName": "Job",
    "cellRenderer": jobPostingCellRenderer,
  },
  { "field": 'created_at' },
  {
    "field": 'download',
    "cellRenderer": DownloadCellRenderer,
    "width": 100
  },
];

export default function TailoredResumeTable() {
  const { getTailoredUserResumes } = useResumeApi();

  const [rowData, setRowData] = useState<RowData[]>([]);

  const autoSizeStrategy = useMemo<
    | SizeColumnsToFitGridStrategy
    | SizeColumnsToFitProvidedWidthStrategy
    | SizeColumnsToContentStrategy
  >(() => ({
    type: "fitCellContents",
  }), [],
  );

  useEffect(() => {
    const fetchTailoredResumeData = async () => {
      try {
        const response = await getTailoredUserResumes();
        const tailoredResumeData = await response.json();

        if (!response.ok) {
          throw new Error("Failed to fetch tailored resumes");
        }

        if (!Array.isArray(tailoredResumeData)) {
          throw new Error("Tailored resume response improperly formatted");
        }

        // TODO switch from typecasting once we have landed on a final table format
        if (tailoredResumeData) {
          setRowData(tailoredResumeData as RowData[]);
        }
      } catch (err) {
        console.error('Fetch error:', err);
      }
    };

    fetchTailoredResumeData();
  }, []);

  return (
    <div className="form-field">
      <label>Tailored Resumes:</label>
      <div className="grid" style={{ height: 200 }}>
        <AgGridReact
          rowData={rowData}
          columnDefs={colDefs}
          autoSizeStrategy={autoSizeStrategy}
          domLayout="autoHeight"
        />
      </div>
    </div>
  );
};

function jobPostingCellRenderer({ data }: CustomCellRendererProps) {
  return (
    <a href={data.job_posting} target="_blank" rel="noopener noreferrer">
      Link
    </a>
  );
};
