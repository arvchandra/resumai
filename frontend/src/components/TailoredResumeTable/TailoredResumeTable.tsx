import { useEffect, useMemo } from "react";

import { AgGridReact } from 'ag-grid-react'; // React Data Grid Component
import type { CustomCellRendererProps } from 'ag-grid-react';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import type {
  SizeColumnsToFitGridStrategy,
  SizeColumnsToFitProvidedWidthStrategy,
  SizeColumnsToContentStrategy
} from 'ag-grid-community';

import { useTailoredResumesContext } from "../../contexts/TailoredResumesContext.tsx";
import DownloadCellRenderer from './DownloadCellRenderer.tsx';

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
    "field": 'job_posting_url',
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
  const {
    tailoredResumes,
    fetchTailoredResumes,
  } = useTailoredResumesContext();

  const autoSizeStrategy = useMemo<
    | SizeColumnsToFitGridStrategy
    | SizeColumnsToFitProvidedWidthStrategy
    | SizeColumnsToContentStrategy
  >(() => ({
    type: "fitCellContents",
  }), [],
  );

  // Fetch tailored resumes on initial load
  useEffect(() => {
    fetchTailoredResumes();
  }, []);

  return (
    <div className="form-field">
      <label>Tailored Resumes:</label>
      <div className="grid" style={{ height: 200 }}>
        <AgGridReact
          rowData={tailoredResumes as RowData[]}
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
    <a href={data.job_posting_url} target="_blank" rel="noopener noreferrer">
      Link
    </a>
  );
};
