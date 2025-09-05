import { useEffect, useMemo } from "react";

import type {
  SizeColumnsToContentStrategy,
  SizeColumnsToFitGridStrategy,
  SizeColumnsToFitProvidedWidthStrategy
} from "ag-grid-community";
import { AllCommunityModule, ModuleRegistry } from "ag-grid-community";
import type { CustomCellRendererProps } from "ag-grid-react";
import { AgGridReact } from "ag-grid-react"; // React Data Grid Component
import { format } from "date-fns";

import { useTailoredResumesContext } from "../../contexts/TailoredResumesContext.tsx";
import ActionsCellRenderer from "./ActionsCellRenderer.tsx";

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
  {
    "field": "actions",
    "headerName": "",
    "cellRenderer": ActionsCellRenderer,
  }
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
      <div className="grid" style={{ height: 255 }}>
        <AgGridReact
          rowData={tailoredResumes as RowData[]}
          columnDefs={colDefs}
          autoSizeStrategy={autoSizeStrategy}
          headerHeight={0}
        />
      </div>
    </div>
  );
};

function dateCreatedCellRenderer({ data }: CustomCellRendererProps) {
  const dateCreated = new Date(data.created_at);
  const formattedDateCreated = format(dateCreated, "MMM do, yyyy");

  return (
    <span>{formattedDateCreated}</span>
  );
}
