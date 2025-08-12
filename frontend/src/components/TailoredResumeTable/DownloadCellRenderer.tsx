import type { ICellRendererParams } from 'ag-grid-community';

import { useResumeApi } from "../../api/resumeApi.ts";

import fileDownloadIcon from "../../assets/images/download-file-icon.png";

const DownloadCellRenderer = ({ data }: ICellRendererParams) => {
  const { downloadTailoredUserResume } = useResumeApi();

  const handleDownloadClick = async (tailoredResumeId: number, tailoredResumeName: string) => {
    try {
      // TODO replace with current user
      const response = await downloadTailoredUserResume(tailoredResumeId);

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Failed to download resume");
      }

      // Create a temporary link to trigger the download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = tailoredResumeName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <img
      className="icon"
      src={fileDownloadIcon}
      alt="Download"
      onClick={() => handleDownloadClick(data.id, data.name)}
    />
  );
};

export default DownloadCellRenderer
