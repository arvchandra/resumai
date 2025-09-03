import useFetchWithAuth from '../hooks/useFetchWithAuth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const TAILOR_API_BASE_URL = `${API_BASE_URL}/tailor`;

export function useResumeApi() {
  const fetchWithAuth = useFetchWithAuth();

  return {
    getUserResumes() {
      return fetchWithAuth(`${TAILOR_API_BASE_URL}/resumes/`);
    },
    uploadUserResume(formData: FormData) {
      return fetchWithAuth(`${TAILOR_API_BASE_URL}/resumes/upload/`, {
        method: "POST",
        body: formData
      });
    },
    tailorUserResume(resumeId: number, jobPostingUrl: string) {
      return fetchWithAuth(`${TAILOR_API_BASE_URL}/tailor-resume/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resume_id: resumeId,
          job_posting_url: jobPostingUrl
        })
      });
    },
    getTailoredUserResumes() {
      return fetchWithAuth(`${TAILOR_API_BASE_URL}/tailored-resumes/`);
    },
    downloadTailoredUserResume(tailoredResumeId: number) {
      return fetchWithAuth(`${TAILOR_API_BASE_URL}/tailored-resume/${tailoredResumeId}/download/`);
    }
  };
}
