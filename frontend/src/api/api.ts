import { useAuth } from '../contexts/AuthContext';
import useFetchWithAuth from '../hooks/useFetchWithAuth';

import type { User } from "../contexts/AuthContext";
import type { fetchWithAuthSignature } from '../hooks/useFetchWithAuth';

const API_BASE = import.meta.env.VITE_API_BASE_URL;
const AUTH_API_BASE = `${API_BASE}/auth`;
const TAILOR_API_BASE = `${API_BASE}/tailor`;

function createAuthenticatedApi(userInfo: User | null, fetchWithAuth: fetchWithAuthSignature) {
  return {
    getUserResumes() {
      return fetchWithAuth(`${TAILOR_API_BASE}/users/${userInfo?.id}/resumes/`);
    },
    uploadUserResume(formData: FormData) {
      return fetchWithAuth(`${TAILOR_API_BASE}/users/${userInfo!.id}/resumes/upload/`, {
        method: "POST",
        body: formData
      });
    },
    tailorResume(resumeId: number, jobPostingUrl: string) {
      return fetchWithAuth(`${TAILOR_API_BASE}/users/${userInfo!.id}/tailor-resume/`, {
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
    getTailoredResumes() {
      return fetchWithAuth(`${TAILOR_API_BASE}/users/${userInfo!.id}/tailored-resumes/`)
    },
    downloadTailoredResume(tailoredResumeId: number) {
      return fetchWithAuth(`${TAILOR_API_BASE}/users/${userInfo!.id}/tailored-resume/${tailoredResumeId}/download/`);
    }
  };
}

export function useAuthenticatedApi() {
  const { userInfo } = useAuth();
  const fetchWithAuth = useFetchWithAuth();

  return createAuthenticatedApi(userInfo, fetchWithAuth);
}

export function useUnauthenticatedApi() {
  return {
    login(googleAccessToken: string) {
      return fetch(`${AUTH_API_BASE}/google-login/`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ googleAccessToken: googleAccessToken }),
      });
    },
    logout() {
      return fetch(`${AUTH_API_BASE}/logout/`, {
        method: "POST",
        credentials: "include", // This includes the refresh token cookie with the request
      });
    },
    refreshToken() {
      return fetch(`${AUTH_API_BASE}/token/refresh/`, {
        method: "POST",
        credentials: "include", // This includes the refresh token cookie with the request
      })
    },
  };
}