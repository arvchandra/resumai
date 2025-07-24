import type { ICellRendererParams } from 'ag-grid-community';
import useFetchWithAuth from "../../hooks/useFetchWithAuth";
import fileDownloadIcon from "../../assets/images/download-file-icon.png";

const DownloadCellRenderer = ({ data }: ICellRendererParams) => {
  const fetchWithAuth = useFetchWithAuth();

  const handleDownloadClick = async (tailoredResumeId: number, tailoredResumeName: string) => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // TODO replace with current user
      const response = await fetchWithAuth(`http://localhost:8000/tailor/users/2/tailor-resume/${tailoredResumeId}/download`);

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Failed to download resume");
      }

      const blob = await response.blob();

      // Create a temporary link to trigger the download
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
      className="action-icon-download"
      src={fileDownloadIcon}
      width={15}
      height={15}
      alt="Download"
      onClick={() => handleDownloadClick(data.id, data.name)}
    />
  );
};

export default DownloadCellRenderer
