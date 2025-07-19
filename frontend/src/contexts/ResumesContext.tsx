import React, { createContext, useCallback, useContext, useEffect, useReducer } from "react";

import useFetchWithAuth from "../hooks/useFetchWithAuth";

import type Resume from "../interfaces/Resume";

interface ResumesState {
  resumes: Resume[];
  selectedResume: Resume | null;
  isFetchingResumes: boolean;
  tempUploadedResumeFile: File | null;
  error: string;
}

interface ResumesMethods {
  fetchResumes: () => Promise<void>;
  addUploadedResume: (resume: Resume) => void;
  setSelectedResume: (resume: Resume) => void;
  setTempUploadedResumeFile: (file: File | null) => void;
}

const resumesInitialState: ResumesState = {
  resumes: [],
  selectedResume: null,
  isFetchingResumes: false,
  tempUploadedResumeFile: null,
  error: '',
}

type ResumesContextType = ResumesState & ResumesMethods;

export const ResumesContext = createContext<ResumesContextType | undefined>(undefined)

type ResumesAction =
  | {type: 'FETCH_START' }
  | {type: 'FETCH_STOP' }
  | {type: 'SET_RESUMES'; payload: Resume[]; }
  | {type: 'SET_SELECTED_RESUME'; payload: Resume; }
  | {type: 'SET_SELECTED_RESUME_IF_NONE'; payload: Resume; }
  | {type: 'SET_TEMP_UPLOADED_RESUME_FILE', payload: File | null; }
  | {type: 'ADD_UPLOADED_RESUME', payload: Resume; }
  | {type: 'SET_ERROR', payload: string; };

function resumesReducer(state: ResumesState, action: ResumesAction) {
  if (action.type == "FETCH_START") {
    return {
      ...state,
      isFetchingResumes: true,
    }
  }
  if (action.type == "FETCH_STOP") {
    return {
      ...state,
      isFetchingResumes: false,
    }
  }
  if (action.type == "SET_RESUMES") {
    // Reset the selected resume to null since the 
    // set of resumes has been refreshed.
    return {
      ...state,
      resumes: action.payload,
      selectedResume: null,
    }
  }
  if (action.type == "SET_SELECTED_RESUME") {
    return {
      ...state,
      selectedResume: action.payload,
    }
  }
  if (action.type == "SET_SELECTED_RESUME_IF_NONE") {
    if (state.selectedResume) return state;
    return {
      ...state,
      selectedResume: action.payload,
    }
  }
  if (action.type == "SET_TEMP_UPLOADED_RESUME_FILE") {
    return {
      ...state,
      tempUploadedResumeFile: action.payload,
    }
  }
  if (action.type == "ADD_UPLOADED_RESUME") {
    const newResumes = [...state.resumes];
    return {
      ...state,
      resumes: [...newResumes, action.payload],
    }
  }
  if (action.type == "SET_ERROR") {
    return {
      ...state,
      error: action.payload,
    }
  }

  return state;
}

export const ResumesContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [resumesState, resumesDispatch] = useReducer(resumesReducer, resumesInitialState);
  const fetchWithAuth = useFetchWithAuth();

  const handleSetSelectedResume = (resume: Resume) => {
    resumesDispatch({
      type: "SET_SELECTED_RESUME",
      payload: resume,
    })
  };

  const handleSetTempUploadedResumeFile = (file: File | null) => {
    resumesDispatch({
      type: "SET_TEMP_UPLOADED_RESUME_FILE",
      payload: file,
    })
  };

  const handleAddUploadedResume = (resume: Resume) => {
    resumesDispatch({
      type: "ADD_UPLOADED_RESUME",
      payload: resume,
    })
  };

  // Async resumes fetching function
  const fetchResumes = useCallback(async () => {
    resumesDispatch({type: "FETCH_START"});
    await new Promise((resolve) => setTimeout(resolve, 1000));
    try {
      const response = await fetchWithAuth("http://localhost:8000/tailor/users/2/resumes/");
      const data: Resume[] = await response.json();
      resumesDispatch({type: "SET_RESUMES", payload: data});

      // Set default resume as selected resume only if no
      // resume had previously been selected (i.e. initial load)
      const default_resume = data.find(resume => resume.is_default);
      if (default_resume) {
        resumesDispatch({
          type: "SET_SELECTED_RESUME_IF_NONE",
          payload: default_resume,
        })
      }
    } catch (error) {
      if (error instanceof Error) {
        resumesDispatch({type: "SET_ERROR", payload: error.message});
      } else {
        resumesDispatch({type: "SET_ERROR", payload: "An error occurred."});
      }
    }
    
    resumesDispatch({type: "FETCH_STOP"});
  }, []);

  // Fetch resumes on initial context load
  useEffect(() => {
    fetchResumes();
  }, [fetchResumes]);

  const ctxValue = {
    resumes: resumesState.resumes,
    selectedResume: resumesState.selectedResume,
    isFetchingResumes: resumesState.isFetchingResumes,
    tempUploadedResumeFile: resumesState.tempUploadedResumeFile,
    error: resumesState.error,
    fetchResumes,
    addUploadedResume: handleAddUploadedResume,
    setSelectedResume: handleSetSelectedResume,
    setTempUploadedResumeFile: handleSetTempUploadedResumeFile,
  }

  return (
    <ResumesContext.Provider value={ctxValue} >
      {children}
    </ResumesContext.Provider>
  )
}

export const useResumesContext = (): ResumesContextType => {
  const context = useContext(ResumesContext);
  if (!context) throw new Error('useResumesContext must be used within ResumesContextProvider');
  return context;
};
