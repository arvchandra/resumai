import React, { createContext, useCallback, useContext, useReducer } from "react";

import type Resume from "../interfaces/Resume";

type ResumesContextType = {
  resumes: Resume[];
  selectedResume: Resume | null;
  isFetchingResumes: boolean;
  setResumes: (resumes: Resume[]) => void;
  setSelectedResume: (resume: Resume) => void;
  setIsFetchingResumes: (isFetching: boolean) => void;
}

export const ResumesContext = createContext<ResumesContextType>({
  resumes: [],
  selectedResume: null,
  isFetchingResumes: false,
  setResumes: () => {},
  setSelectedResume: () => {},
  setIsFetchingResumes: () => {},
})

type ResumesState = {
  resumes: Resume[];
  selectedResume: Resume | null;
  isFetchingResumes: boolean;
}

type ResumesAction =
  | {type: 'SET_RESUMES'; payload: Resume[]; }
  | {type: 'SET_SELECTED_RESUME'; payload: Resume; }
  | {type: 'SET_IS_FETCHING_RESUMES'; payload: boolean; };

function resumesReducer(state: ResumesState, action: ResumesAction) {
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
  if (action.type == "SET_IS_FETCHING_RESUMES") {
    return {
      ...state,
      isFetchingResumes: action.payload,
    }
  }

  return state;
}

export const ResumesContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [resumesState, resumesDispatch] = useReducer(resumesReducer, {
    resumes: [],
    selectedResume: null,
    isFetchingResumes: false,
  })

  const handleSetResumes = useCallback((resumes: Resume[]) => {
    resumesDispatch({
      type: "SET_RESUMES",
      payload: resumes,
    })
  }, []);

  const handleSetSelectedResume = (resume: Resume) => {
    resumesDispatch({
      type: "SET_SELECTED_RESUME",
      payload: resume,
    })
  };

  const handleSetIsFetchingResumes = useCallback((isFetching: boolean) => {
    resumesDispatch({
      type: "SET_IS_FETCHING_RESUMES",
      payload: isFetching,
    })
  }, []);

  const ctxValue = {
    resumes: resumesState.resumes,
    selectedResume: resumesState.selectedResume,
    isFetchingResumes: resumesState.isFetchingResumes,
    setResumes: handleSetResumes,
    setSelectedResume: handleSetSelectedResume,
    setIsFetchingResumes: handleSetIsFetchingResumes,
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